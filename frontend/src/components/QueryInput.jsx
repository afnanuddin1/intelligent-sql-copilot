import { useState } from 'react'
import { runQuery } from '../api/client'
import useQueryStore from '../store/queryStore'

const EXAMPLES = [
  'Which airlines have the most flights?',
  'What are the most delayed routes on average?',
  'Show me all cancelled flights',
  'Which aircraft model is used most frequently?',
  'What is the average review rating per airline?',
  'Show top 10 routes by distance',
]

export default function QueryInput() {
  const [input, setInput] = useState('')
  const { isLoading, setLoading, setResult, setError } = useQueryStore()

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return
    setLoading(true)
    setError(null)
    try {
      const res = await runQuery(input.trim())
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit()
  }

  return (
    <div className="query-input-card">
      <div className="input-header">
        <span className="input-label">✦ QUERY</span>
        <span className="input-hint">Ctrl+Enter to run</span>
      </div>
      <textarea
        className="query-textarea"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKey}
        placeholder="Ask anything about your flight data..."
        rows={3}
      />
      <div className="input-footer">
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="example-chip" onClick={() => setInput(ex)}>
              {ex}
            </button>
          ))}
        </div>
        <button
          className={`run-btn ${isLoading ? 'loading' : ''}`}
          onClick={handleSubmit}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? <span className="spinner" /> : '▶ RUN'}
        </button>
      </div>
    </div>
  )
}