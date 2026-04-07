import { useEffect } from 'react'
import { getHistory } from '../api/client'
import useQueryStore from '../store/queryStore'

export default function QueryHistory() {
  const { history, historyLoading, setHistory, setHistoryLoading, setPendingInput } = useQueryStore()

  useEffect(() => {
    const load = async () => {
      setHistoryLoading(true)
      try {
        const res = await getHistory()
        setHistory(res.data)
      } catch (e) {
        console.error(e)
      } finally {
        setHistoryLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div className="history-panel">
      <div className="history-header">
        <span>◷ HISTORY</span>
      </div>
      {historyLoading ? (
        <p className="history-loading">Loading...</p>
      ) : history.length === 0 ? (
        <p className="history-empty">No queries yet</p>
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div key={item.id} className="history-item" onClick={() => setPendingInput(item.natural_language)}>
              <p className="history-nl">{item.natural_language}</p>
              <div className="history-meta">
                <span>{item.execution_time_ms?.toFixed(0)}ms</span>
                <span>{item.rows_returned} rows</span>
                {item.had_seq_scan && <span className="history-seq">SEQ</span>}
                {item.was_cached && <span className="history-cached">⚡</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}