from app.models import MetadataResponse, QueryRequest


def _q(identifier: str) -> str:
    # MVP: metadados vêm do catálogo do banco; validação conservadora para nomes SQL.
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_$#")
    if not identifier or any(ch not in allowed for ch in identifier):
        raise ValueError(f"Identificador inválido: {identifier}")
    return identifier


def build_query(request: QueryRequest, metadata: MetadataResponse) -> str:
    table_map = {t.name: t for t in metadata.tables}

    for table in request.tables:
        if table not in table_map:
            raise ValueError(f"Tabela desconhecida: {table}")

    aliases = {table: f"t{i+1}" for i, table in enumerate(request.tables)}
    selected_parts = []
    for item in request.columns:
        if item.table not in table_map:
            raise ValueError(f"Tabela desconhecida: {item.table}")
        valid_cols = {c.name for c in table_map[item.table].columns}
        if item.column not in valid_cols:
            raise ValueError(f"Coluna desconhecida: {item.table}.{item.column}")
        part = f"{aliases[item.table]}.{_q(item.column)}"
        if item.alias:
            part += f" AS {_q(item.alias)}"
        selected_parts.append(part)

    base_table = request.tables[0]
    base_meta = table_map[base_table]
    sql = [
        "SELECT",
        "    " + ",\n    ".join(selected_parts),
        f"FROM {_q(base_meta.schema_name)}.{_q(base_table)} {aliases[base_table]}",
    ]

    joined = {base_table}
    remaining = set(request.tables[1:])

    while remaining:
        joined_one = False
        for rel in metadata.relationships:
            a = rel.from_table
            b = rel.to_table

            if a in remaining and b in joined:
                child, parent = a, b
                child_cols, parent_cols = rel.from_columns, rel.to_columns
            elif b in remaining and a in joined:
                child, parent = b, a
                child_cols, parent_cols = rel.to_columns, rel.from_columns
            else:
                continue

            conditions = [
                f"{aliases[child]}.{_q(c)} = {aliases[parent]}.{_q(p)}"
                for c, p in zip(child_cols, parent_cols)
            ]
            meta = table_map[child]
            sql.append(
                f"JOIN {_q(meta.schema_name)}.{_q(child)} {aliases[child]}\n"
                f"  ON " + "\n AND ".join(conditions)
            )
            joined.add(child)
            remaining.remove(child)
            joined_one = True
            break

        if not joined_one:
            missing = ", ".join(sorted(remaining))
            raise ValueError(
                f"Não foi possível encontrar relacionamento para: {missing}. "
                "Cadastre um relacionamento manual ou escolha tabelas conectadas."
            )

    return "\n".join(sql)
