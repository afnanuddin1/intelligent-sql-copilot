import useQueryStore from '../store/queryStore'

const SEVERITY_COLORS = { ok: '#4ade80', warning: '#facc15', critical: '#f87171' }

export default function OptimizationPanel() {
  const result = useQueryStore((s) => s.result)
  if (!result?.optimizations) return null

  const { severity, suggestions, rewritten_sql, cost_comparison } = result.optimizations

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">⚡ OPTIMIZATIONS</span>
        <span className="severity-badge" style={{ color: SEVERITY_COLORS[severity] }}>
          {severity.toUpperCase()}
        </span>
      </div>
      {suggestions.length === 0 ? (
        <p className="no-suggestions">✓ No issues detected — query looks good!</p>
      ) : (
        <div className="suggestions">
          {suggestions.map((s, i) => (
            <div key={i} className="suggestion-card">
              <div className="suggestion-header">
                <span className="suggestion-type">{s.type.replace(/_/g, ' ').toUpperCase()}</span>
                {s.table && <span className="suggestion-table">{s.table}</span>}
              </div>
              <p className="suggestion-reason">{s.reason}</p>
              {s.ddl && (
                <pre className="suggestion-ddl">{s.ddl}</pre>
              )}
            </div>
          ))}
        </div>
      )}
      {cost_comparison && (
        <div className="cost-comparison">
          <span>Original cost: <strong>{cost_comparison.original?.toFixed(2)}</strong></span>
          {cost_comparison.estimated_rewritten && (
            <span>Rewritten cost: <strong>{cost_comparison.estimated_rewritten?.toFixed(2)}</strong></span>
          )}
        </div>
      )}
    </div>
  )
}