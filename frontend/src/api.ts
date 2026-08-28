import type { MetadataResponse, SelectedField } from './types'

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function loadMetadata(): Promise<MetadataResponse> {
  const response = await fetch(`${API}/api/metadata`)
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return response.json()
}

export async function generateSql(tables: string[], columns: SelectedField[]): Promise<string> {
  const response = await fetch(`${API}/api/query/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tables, columns, limit: 100 }),
  })
  const payload = await response.json()
  if (!response.ok) {
    throw new Error(payload.detail ?? 'Falha ao gerar SQL')
  }
  return payload.sql
}

export async function executeSql(sql: string): Promise<{ columns: string[]; rows: unknown[][] }> {
  const response = await fetch(`${API}/api/query/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sql, limit: 100 }),
  })
  const payload = await response.json()
  if (!response.ok) {
    throw new Error(payload.detail ?? 'Falha ao executar SQL')
  }
  return payload
}
