import re

import pyodbc

from app.config import settings
from app.models import ColumnMeta, MetadataResponse, RelationshipMeta, TableMeta


class SqlServerAdapter:
    def _connect(self):
        conn_str = (
            f"DRIVER={{{settings.odbc_driver}}};"
            f"SERVER={settings.db_host},{settings.db_port or 1433};"
            f"DATABASE={settings.db_database};"
            f"UID={settings.db_user};PWD={settings.db_password};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(conn_str)

    def get_metadata(self) -> MetadataResponse:
        schema = settings.db_schema or "dbo"

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                '''
                SELECT t.TABLE_NAME, t.TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE t.TABLE_SCHEMA = ?
                ORDER BY t.TABLE_NAME
                ''',
                schema,
            )
            objects = cur.fetchall()

            cur.execute(
                '''
                SELECT c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS c
                WHERE c.TABLE_SCHEMA = ?
                ORDER BY c.TABLE_NAME, c.ORDINAL_POSITION
                ''',
                schema,
            )
            col_rows = cur.fetchall()

            cur.execute(
                '''
                SELECT ku.TABLE_NAME, ku.COLUMN_NAME
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
                JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE ku
                  ON ku.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
                 AND ku.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA
                WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
                  AND tc.TABLE_SCHEMA = ?
                ''',
                schema,
            )
            pk_rows = {(r[0], r[1]) for r in cur.fetchall()}

            cur.execute(
                '''
                SELECT
                    fk.name,
                    OBJECT_NAME(fkc.parent_object_id) child_table,
                    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) child_column,
                    OBJECT_NAME(fkc.referenced_object_id) parent_table,
                    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) parent_column,
                    fkc.constraint_column_id
                FROM sys.foreign_keys fk
                JOIN sys.foreign_key_columns fkc
                  ON fkc.constraint_object_id = fk.object_id
                JOIN sys.tables t
                  ON t.object_id = fkc.parent_object_id
                JOIN sys.schemas s
                  ON s.schema_id = t.schema_id
                WHERE s.name = ?
                ORDER BY fk.name, fkc.constraint_column_id
                ''',
                schema,
            )
            fk_rows = cur.fetchall()

        columns_by_table: dict[str, list[ColumnMeta]] = {}
        for table, column, data_type, nullable in col_rows:
            columns_by_table.setdefault(table, []).append(
                ColumnMeta(
                    name=column,
                    data_type=data_type,
                    nullable=nullable == "YES",
                    primary_key=(table, column) in pk_rows,
                )
            )

        tables = [
            TableMeta(
                schema_name=schema,
                name=name,
                kind="VIEW" if table_type == "VIEW" else "TABLE",
                columns=columns_by_table.get(name, []),
            )
            for name, table_type in objects
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

        safe_sql = f"SELECT TOP ({int(limit)}) * FROM ({sql.rstrip().rstrip(';')}) q"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(safe_sql)
            columns = [d[0] for d in cur.description]
            rows = [list(r) for r in cur.fetchall()]
        return columns, rows
