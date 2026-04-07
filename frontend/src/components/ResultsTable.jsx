import useQueryStore from '../store/queryStore'

export default function ResultsTable() {
  const result = useQueryStore((s) => s.result)
  if (!result?.results) return null

  const { columns, rows, total_rows } = result.results

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">▦ RESULTS</span>
        <span className="row-count">{total_rows} rows</span>
      </div>
      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>{columns.map((col) => <th key={col}>{col}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j}>
                    {cell === null
                      ? <span className="null-val">NULL</span>
                      : typeof cell === 'number' && !Number.isInteger(cell)
                        ? parseFloat(cell.toFixed(2))
                        : typeof cell === 'string' && /^\d+\.\d{5,}$/.test(cell)
                          ? parseFloat(parseFloat(cell).toFixed(2))
                          : String(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}