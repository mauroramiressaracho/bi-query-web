import re

import oracledb

from app.config import settings
from app.models import ColumnMeta, MetadataResponse, RelationshipMeta, TableMeta


class OracleAdapter:
    def _connect(self):
        dsn = oracledb.makedsn(
            settings.db_host,
            settings.db_port or 1521,
            service_name=settings.db_service,
        )
        return oracledb.connect(
            user=settings.db_user,
            password=settings.db_password,
            dsn=dsn,
        )

    def get_metadata(self) -> MetadataResponse:
        schema = (settings.db_schema or settings.db_user).upper()

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT table_name, 'TABLE' kind
                    FROM all_tables
                    WHERE owner = :owner
                    UNION ALL
                    SELECT view_name, 'VIEW' kind
                    FROM all_views
                    WHERE owner = :owner
                    ORDER BY 1
                    ''',
                    owner=schema,
                )
                objects = cur.fetchall()

                cur.execute(
                    '''
                    SELECT table_name, column_name, data_type, nullable
                    FROM all_tab_columns
                    WHERE owner = :owner
                    ORDER BY table_name, column_id
                    ''',
                    owner=schema,
                )
                col_rows = cur.fetchall()

                cur.execute(
                    '''
                    SELECT acc.table_name, acc.column_name
                    FROM all_constraints ac
                    JOIN all_cons_columns acc
                      ON acc.owner = ac.owner
                     AND acc.constraint_name = ac.constraint_name
                    WHERE ac.owner = :owner
                      AND ac.constraint_type = 'P'
                    ''',
                    owner=schema,
                )
                pk_rows = {(r[0], r[1]) for r in cur.fetchall()}

                cur.execute(
                    '''
                    SELECT
                        a.constraint_name,
                        a.table_name child_table,
                        acc.column_name child_column,
                        c_pk.table_name parent_table,
                        acc_pk.column_name parent_column,
                        acc.position
                    FROM all_constraints a
                    JOIN all_cons_columns acc
                      ON acc.owner = a.owner
                     AND acc.constraint_name = a.constraint_name
                    JOIN all_constraints c_pk
                      ON c_pk.owner = a.r_owner
                     AND c_pk.constraint_name = a.r_constraint_name
                    JOIN all_cons_columns acc_pk
                      ON acc_pk.owner = c_pk.owner
                     AND acc_pk.constraint_name = c_pk.constraint_name
                     AND acc_pk.position = acc.position
                    WHERE a.owner = :owner
                      AND a.constraint_type = 'R'
                    ORDER BY a.constraint_name, acc.position
                    ''',
                    owner=schema,
                )
                fk_rows = cur.fetchall()

        columns_by_table: dict[str, list[ColumnMeta]] = {}
        for table, column, data_type, nullable in col_rows:
            columns_by_table.setdefault(table, []).append(
                ColumnMeta(
                    name=column,
                    data_type=data_type,
                    nullable=nullable == "Y",
                    primary_key=(table, column) in pk_rows,
                )
            )

        tables = [
            TableMeta(
                schema_name=schema,
                name=name,
                kind=kind,
                columns=columns_by_table.get(name, []),
            )
            for name, kind in objects
        ]

        grouped: dict[str, dict] = {}
        for constraint, child_table, child_column, parent_table, parent_column, _ in fk_rows:
            item = grouped.setdefault(
                constraint,
                {
                    "from_table": child_table,
                    "from_columns": [],
                    "to_table": parent_table,
                    "to_columns": [],
                },
            )
            item["from_columns"].append(child_column)
            item["to_columns"].append(parent_column)

        relationships = [
            RelationshipMeta(
                name=name,
                from_schema=schema,
                from_table=v["from_table"],
                from_columns=v["from_columns"],
                to_schema=schema,
                to_table=v["to_table"],
                to_columns=v["to_columns"],
            )
            for name, v in grouped.items()
        ]

        return MetadataResponse(tables=tables, relationships=relationships)

    def execute_select(self, sql: str, limit: int):
        if not re.match(r"^\s*select\b", sql, re.IGNORECASE):
            raise ValueError("Apenas consultas SELECT são permitidas.")

        safe_sql = f"SELECT * FROM ({sql.rstrip().rstrip(';')}) WHERE ROWNUM <= :max_rows"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(safe_sql, max_rows=limit)
                columns = [d[0] for d in cur.description]
                rows = [list(r) for r in cur.fetchall()]
        return columns, rows
