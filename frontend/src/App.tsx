import { useEffect, useMemo, useState } from 'react'
import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node,
  useEdgesState,
  useNodesState,
} from '@xyflow/react'

import { executeSql, generateSql, loadMetadata } from './api'
import TableNode from './TableNode'
import type { MetadataResponse, SelectedField, TableMeta } from './types'

const nodeTypes = { table: TableNode }

function makeNode(
  table: TableMeta,
  index: number,
  selected: Set<string>,
  onToggle: (table: string, column: string) => void,
): Node {
  return {
    id: table.name,
    type: 'table',
    position: { x: 80 + (index % 3) * 360, y: 80 + Math.floor(index / 3) * 360 },
    data: { table, selected, onToggle },
  }
}

export default function App() {
  const [metadata, setMetadata] = useState<MetadataResponse>({ tables: [], relationships: [] })
  const [activeTables, setActiveTables] = useState<string[]>([])
  const [selectedFields, setSelectedFields] = useState<SelectedField[]>([])
  const [sql, setSql] = useState('')
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [result, setResult] = useState<{ columns: string[]; rows: unknown[][] } | null>(null)
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const selectedSet = useMemo(
    () => new Set(selectedFields.map((x) => `${x.table}.${x.column}`)),
    [selectedFields],
  )

  useEffect(() => {
    loadMetadata()
      .then(setMetadata)
      .catch((e) => setError(String(e)))
  }, [])

  function toggleField(table: string, column: string) {
    setSelectedFields((current) => {
      const exists = current.some((x) => x.table === table && x.column === column)
      if (exists) return current.filter((x) => !(x.table === table && x.column === column))
      return [...current, { table, column }]
    })
  }

  function addTable(name: string) {
    setActiveTables((current) => (current.includes(name) ? current : [...current, name]))
  }

  function removeTable(name: string) {
    setActiveTables((current) => current.filter((x) => x !== name))
    setSelectedFields((current) => current.filter((x) => x.table !== name))
  }

  useEffect(() => {
    const selectedTables = metadata.tables.filter((t) => activeTables.includes(t.name))

    setNodes((current) => {
      const previousPositions = new Map(current.map((n) => [n.id, n.position]))
      return selectedTables.map((table, index) => {
        const node = makeNode(table, index, selectedSet, toggleField)
        const pos = previousPositions.get(table.name)
        return pos ? { ...node, position: pos } : node
      })
    })

    const nextEdges = metadata.relationships
      .filter((r) => activeTables.includes(r.from_table) && activeTables.includes(r.to_table))
      .map((r) => ({
        id: r.name,
        source: r.from_table,
        target: r.to_table,
        label: r.from_columns.join(', ') + ' → ' + r.to_columns.join(', '),
        animated: false,
      }))
    setEdges(nextEdges)
  }, [metadata, activeTables, selectedSet])

  useEffect(() => {
    if (!activeTables.length || !selectedFields.length) {
      setSql('')
      return
    }

    const timer = window.setTimeout(() => {
      generateSql(activeTables, selectedFields)
        .then((generated) => {
          setSql(generated)
          setError('')
        })
        .catch((e) => setError(e.message))
    }, 150)

    return () => window.clearTimeout(timer)
  }, [activeTables, selectedFields])

  async function runQuery() {
    if (!sql) return
    try {
      setResult(await executeSql(sql))
      setError('')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  const filteredTables = metadata.tables.filter((t) =>
    t.name.toLowerCase().includes(search.toLowerCase()),
  )

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>BI Query Web</h1>
          <p>Construtor visual de consultas</p>
        </div>
        <span className="badge">MVP 0.1</span>
      </header>

      {error && <div className="error">{error}</div>}

      <main className="workspace">
        <aside className="sidebar">
          <input
            className="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Pesquisar tabela..."
          />

          <div className="tree-title">OBJETOS DO BANCO</div>
          <div className="tree">
            {filteredTables.map((table) => {
              const active = activeTables.includes(table.name)
              return (
                <div key={table.name} className={`tree-table ${active ? 'active' : ''}`}>
                  <button
                    type="button"
                    className="tree-table__button"
                    onClick={() => (active ? removeTable(table.name) : addTable(table.name))}
                  >
                    <span>{active ? '▾' : '▸'} {table.name}</span>
                    <small>{table.kind}</small>
                  </button>

                  {active && (
                    <div className="tree-columns">
                      {table.columns.map((column) => {
                        const key = `${table.name}.${column.name}`
                        return (
                          <label key={key}>
                            <input
                              type="checkbox"
                              checked={selectedSet.has(key)}
                              onChange={() => toggleField(table.name, column.name)}
                            />
                            <span>{column.primary_key ? '🔑 ' : ''}{column.name}</span>
                          </label>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </aside>

        <section className="main-area">
          <div className="canvas-panel">
            {nodes.length === 0 ? (
              <div className="empty-state">
                <strong>Adicione uma tabela</strong>
                <span>Clique em uma tabela na árvore à esquerda para começar.</span>
              </div>
            ) : (
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
              >
                <Background />
                <Controls />
              </ReactFlow>
            )}
          </div>

          <section className="sql-panel">
            <div className="panel-header">
              <div>
                <strong>SQL gerado</strong>
                <span>{selectedFields.length} campo(s) selecionado(s)</span>
              </div>
              <button type="button" className="run-button" disabled={!sql} onClick={runQuery}>
                ▶ Executar
              </button>
            </div>
            <pre>{sql || '-- Selecione campos para gerar a consulta.'}</pre>
          </section>

          {result && (
            <section className="result-panel">
              <div className="panel-header">
                <div>
                  <strong>Resultado</strong>
                  <span>{result.rows.length} linha(s)</span>
                </div>
              </div>
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>{result.columns.map((c) => <th key={c}>{c}</th>)}</tr>
                  </thead>
                  <tbody>
                    {result.rows.map((row, i) => (
                      <tr key={i}>
                        {row.map((value, j) => <td key={j}>{String(value ?? '')}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}
        </section>
      </main>
    </div>
  )
}
