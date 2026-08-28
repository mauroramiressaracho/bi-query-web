export type ColumnMeta = {
  name: string
  data_type: string
  nullable: boolean
  primary_key: boolean
}

export type TableMeta = {
  schema_name: string
  name: string
  kind: string
  columns: ColumnMeta[]
}

export type RelationshipMeta = {
  name: string
  from_schema: string
  from_table: string
  from_columns: string[]
  to_schema: string
  to_table: string
  to_columns: string[]
}

export type MetadataResponse = {
  tables: TableMeta[]
  relationships: RelationshipMeta[]
}

export type SelectedField = {
  table: string
  column: string
}
