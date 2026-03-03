import { useState } from 'react'
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter'
import sql from 'react-syntax-highlighter/dist/esm/languages/hljs/sql'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'
import useQueryStore from '../store/queryStore'

SyntaxHighlighter.registerLanguage('sql', sql)

export default function SQLDisplay() {
  const result = useQueryStore((s) => s.result)
  const [copied, setCopied] = useState(false)

  if (!result) return null

  const copy = () => {
    navigator.clipboard.writeText(result.generated_sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">⟨/⟩ GENERATED SQL</span>
        <div className="panel-meta">
          <span className={`cache-badge ${result.was_cached ? 'cached' : 'fresh'}`}>
            {result.was_cached ? '⚡ CACHED' : '● FRESH'}
          </span>
          <span className="exec-time">{result.execution_time_ms?.toFixed(1)}ms</span>
          <button className="copy-btn" onClick={copy}>
            {copied ? '✓ COPIED' : 'COPY'}
          </button>
        </div>
      </div>
      <SyntaxHighlighter
        language="sql"
        style={atomOneDark}
        customStyle={{ margin: 0, borderRadius: '0 0 12px 12px', fontSize: '13px', padding: '20px' }}
      >
        {result.generated_sql}
      </SyntaxHighlighter>
    </div>
  )
}