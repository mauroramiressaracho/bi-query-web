from pydantic import BaseModel, Field


class ColumnMeta(BaseModel):
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False


class TableMeta(BaseModel):
    schema_name: str
    name: str
    kind: str = "TABLE"
    columns: list[ColumnMeta]


class RelationshipMeta(BaseModel):
    name: str
    from_schema: str
    from_table: str
    from_columns: list[str]
    to_schema: str
    to_table: str
    to_columns: list[str]


class MetadataResponse(BaseModel):
    tables: list[TableMeta]
    relationships: list[RelationshipMeta]


class SelectedColumn(BaseModel):
    table: str
    column: str
    alias: str | None = None


class QueryRequest(BaseModel):
    tables: list[str] = Field(min_length=1)
    columns: list[SelectedColumn] = Field(min_length=1)
    limit: int = 100


class QueryResponse(BaseModel):
    sql: str


class ExecuteRequest(BaseModel):
    sql: str
    limit: int = 100


class ExecuteResponse(BaseModel):
    columns: list[str]
    rows: list[list[object | None]]
