import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { TableMeta } from './types'

type Data = {
  table: TableMeta
  selected: Set<string>
  onToggle: (table: string, column: string) => void
}

export default function TableNode({ data }: NodeProps) {
  const d = data as unknown as Data

  return (
    <div className="table-node">
      <Handle type="target" position={Position.Left} />
      <div className="table-node__title">
        <span>{d.table.name}</span>
        <small>{d.table.kind}</small>
      </div>

      <div className="table-node__columns">
        {d.table.columns.map((column) => {
          const key = `${d.table.name}.${column.name}`
          return (
            <label key={key} className="column-row">
              <input
                type="checkbox"
                checked={d.selected.has(key)}
                onChange={() => d.onToggle(d.table.name, column.name)}
              />
              <span className={column.primary_key ? 'pk' : ''}>
                {column.primary_key ? '🔑 ' : ''}
                {column.name}
              </span>
              <small>{column.data_type}</small>
            </label>
          )
        })}
      </div>
      <Handle type="source" position={Position.Right} />
    </div>
  )
}
