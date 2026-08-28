from .models import ColumnMeta, MetadataResponse, RelationshipMeta, TableMeta


def get_demo_metadata() -> MetadataResponse:
    tables = [
        TableMeta(
            schema_name="RH",
            name="REG_EMPREGO",
            columns=[
                ColumnMeta(name="EMP_COD", data_type="NUMBER", nullable=False, primary_key=True),
                ColumnMeta(name="CHAPA", data_type="VARCHAR2", nullable=False, primary_key=True),
                ColumnMeta(name="PESSOA_ID", data_type="NUMBER"),
                ColumnMeta(name="ORGAO_ID", data_type="NUMBER"),
                ColumnMeta(name="DT_ADMISSAO", data_type="DATE"),
            ],
        ),
        TableMeta(
            schema_name="RH",
            name="PESSOAS",
            columns=[
                ColumnMeta(name="ID", data_type="NUMBER", nullable=False, primary_key=True),
                ColumnMeta(name="NOME", data_type="VARCHAR2"),
                ColumnMeta(name="CPF", data_type="VARCHAR2"),
            ],
        ),
        TableMeta(
            schema_name="RH",
            name="REG_DESIGNACOES",
            columns=[
                ColumnMeta(name="REMP_EMP_COD", data_type="NUMBER"),
                ColumnMeta(name="REMP_CHAPA", data_type="VARCHAR2"),
                ColumnMeta(name="TPDE_COD", data_type="NUMBER"),
                ColumnMeta(name="DT_INI_VIG", data_type="DATE"),
                ColumnMeta(name="DT_FIM_VIG", data_type="DATE"),
            ],
        ),
        TableMeta(
            schema_name="RH",
            name="ORGAOS",
            columns=[
                ColumnMeta(name="ID", data_type="NUMBER", nullable=False, primary_key=True),
                ColumnMeta(name="NOME", data_type="VARCHAR2"),
            ],
        ),
    ]

    relationships = [
        RelationshipMeta(
            name="FK_REG_EMPREGO_PESSOAS",
            from_schema="RH",
            from_table="REG_EMPREGO",
            from_columns=["PESSOA_ID"],
            to_schema="RH",
            to_table="PESSOAS",
            to_columns=["ID"],
        ),
        RelationshipMeta(
            name="FK_REG_EMPREGO_ORGAOS",
            from_schema="RH",
            from_table="REG_EMPREGO",
            from_columns=["ORGAO_ID"],
            to_schema="RH",
            to_table="ORGAOS",
            to_columns=["ID"],
        ),
        RelationshipMeta(
            name="REL_REG_DESIGNACOES_EMPREGO",
            from_schema="RH",
            from_table="REG_DESIGNACOES",
            from_columns=["REMP_EMP_COD", "REMP_CHAPA"],
            to_schema="RH",
            to_table="REG_EMPREGO",
            to_columns=["EMP_COD", "CHAPA"],
        ),
    ]

    return MetadataResponse(tables=tables, relationships=relationships)
