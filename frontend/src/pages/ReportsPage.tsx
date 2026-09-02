import { useState } from 'react'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

export default function ReportsPage() {
  const [filters, setFilters] = useState({ start_date: '', end_date: '' })
  const [data, setData] = useState<any | null>(null)

  const run = async () => {
    const response = await api.get('/reports/summary', { params: filters })
    setData(response.data)
  }

  return (
    <AppShell title="Reports" intro="Run date-range reports for time saved, district attorney and judge activity, court dates, and intake volume.">
      <section className="panel">
        <div className="toolbar">
          <label>Start date<input type="date" value={filters.start_date} onChange={e => setFilters({ ...filters, start_date: e.target.value })} /></label>
          <label>End date<input type="date" value={filters.end_date} onChange={e => setFilters({ ...filters, end_date: e.target.value })} /></label>
          <button onClick={run}>Run reports</button>
        </div>
      </section>
      {data && (
        <section className="report-grid">
          <article className="report-card"><h3>Time Saved Report</h3><p>{data.time_saved_total} hours</p></article>
          <article className="report-card"><h3>Intake Report</h3><p>{data.intakes_count} intakes</p></article>
          <article className="report-card wide"><h3>DA report</h3><ul className="report-list">{data.by_prosecutor.map((item: any) => <li key={item.prosecutor}>{item.prosecutor}: {item.count}</li>)}</ul></article>
          <article className="report-card wide"><h3>Judge report</h3><ul className="report-list">{data.by_judge.map((item: any) => <li key={item.judge}>{item.judge}: {item.count}</li>)}</ul></article>
          <article className="report-card wide"><h3>Court dates within selected time frame</h3>
            <table className="data-table compact-table">
              <thead><tr><th>Name</th><th>Case</th><th>Date</th><th>Time</th><th>Court</th></tr></thead>
              <tbody>{data.court_dates.map((row: any, idx: number) => <tr key={`${row.case_numbers}-${idx}`}><td>{row.name}</td><td>{row.case_numbers || '—'}</td><td>{row.next_court_date || '—'}</td><td>{row.next_court_time || '—'}</td><td>{row.court_site || '—'}</td></tr>)}</tbody>
            </table>
          </article>
        </section>
      )}
    </AppShell>
  )
}
