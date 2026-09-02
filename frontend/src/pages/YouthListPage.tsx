import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

export default function YouthListPage() {
  const [rows, setRows] = useState<any[]>([])
  const [search, setSearch] = useState('')
  useEffect(() => { api.get('/mis/youth').then((r) => setRows(r.data)) }, [])
  const filtered = useMemo(() => rows.filter((y) => `${y.name} ${y.telephone || ''} ${y.email || ''}`.toLowerCase().includes(search.toLowerCase())), [rows, search])

  return <AppShell title="Youth Directory" intro="Staff see only youth assigned to them. Administrators, managers, and supervisors can view the full program caseload.">
    <div className="toolbar" style={{ marginBottom: '1rem' }}>
      <label className="toolbar-search">Search youth<input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Name, telephone, or email" /></label>
      <Link className="button-link" to="/youth/new">Add youth</Link>
    </div>
    <section className="panel table-wrap">
      <table className="data-table"><thead><tr><th>Name</th><th>Age</th><th>Assigned staff</th><th>Next contact</th><th>Status</th></tr></thead>
        <tbody>{filtered.map((y) => <tr key={y.id}><td><Link to={`/youth/${y.id}`}><strong>{y.name}</strong></Link><div className="muted">{y.telephone || y.email || 'No contact information'}</div></td><td>{y.age ?? '—'}</td><td>{y.assigned_staff_name || 'Unassigned'}</td><td>{y.next_contact_date || '—'}</td><td><span className="status-chip">{y.status}</span></td></tr>)}</tbody>
      </table>
      {filtered.length === 0 && <p className="muted" style={{ padding: '1rem 0' }}>No youth match this search.</p>}
    </section>
  </AppShell>
}
