import QueryInput from './components/QueryInput'
import SQLDisplay from './components/SQLDisplay'
import ResultsTable from './components/ResultsTable'
import QueryPlanTree from './components/QueryPlanTree'
import OptimizationPanel from './components/OptimizationPanel'
import QueryHistory from './components/QueryHistory'
import useQueryStore from './store/queryStore'
import './App.css'

export default function App() {
  const { error } = useQueryStore()

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-icon">✈</span>
          <div>
            <div className="logo-title">SQL COPILOT</div>
            <div className="logo-sub">FLIGHT INTELLIGENCE</div>
          </div>
        </div>
        <QueryHistory />
      </aside>

      <main className="main">
        <header className="topbar">
          <h1 className="topbar-title">Intelligent SQL Copilot</h1>
          <span className="topbar-sub">Natural language → Optimized SQL</span>
        </header>

        <div className="content">
          <QueryInput />
          {error && <div className="error-banner">⚠ {error}</div>}
          <SQLDisplay />
          <div className="panels-row">
            <ResultsTable />
            <QueryPlanTree />
          </div>
          <OptimizationPanel />
        </div>
      </main>
    </div>
  )
}