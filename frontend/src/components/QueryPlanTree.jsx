import useQueryStore from '../store/queryStore'

function getCostColor(cost) {
  if (cost < 100) return '#4ade80'
  if (cost < 1000) return '#facc15'
  return '#f87171'
}

function PlanNode({ node, depth = 0 }) {
  return (
    <div style={{ marginLeft: depth * 20, marginBottom: 8 }}>
      <div className={`plan-node ${node.is_seq_scan ? 'seq-scan' : ''}`}>
        <span className="node-type">{node.node_type}</span>
        {node.relation && <span className="node-relation">→ {node.relation}</span>}
        <span className="node-cost" style={{ color: getCostColor(node.total_cost) }}>
          cost: {node.total_cost.toFixed(2)}
        </span>
        {node.actual_rows != null && (
          <span className="node-rows">{node.actual_rows} rows</span>
        )}
        {node.is_seq_scan && <span className="seq-badge">SEQ SCAN ⚠</span>}
      </div>
    </div>
  )
}

export default function QueryPlanTree() {
  const result = useQueryStore((s) => s.result)
  if (!result?.explain_analysis) return null

  const { total_cost, planning_time_ms, execution_time_ms, nodes, seq_scans } = result.explain_analysis

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">◈ QUERY PLAN</span>
        <div className="plan-stats">
          <span>Total cost: <strong>{total_cost.toFixed(2)}</strong></span>
          <span>Plan: <strong>{planning_time_ms.toFixed(2)}ms</strong></span>
          <span>Exec: <strong>{execution_time_ms.toFixed(2)}ms</strong></span>
        </div>
      </div>
      {seq_scans.length > 0 && (
        <div className="seq-scan-warning">
          ⚠ Sequential scans detected on: <strong>{seq_scans.join(', ')}</strong>
        </div>
      )}
      <div className="plan-tree">
        {nodes.map((node, i) => <PlanNode key={i} node={node} depth={i === 0 ? 0 : 1} />)}
      </div>
    </div>
  )
}