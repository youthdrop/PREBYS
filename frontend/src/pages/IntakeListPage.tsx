import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'
import { useAuth } from '../hooks/useAuth'

export default function IntakeListPage() {
  const { user } = useAuth()
  const [items, setItems] = useState<any[]>([])
  const [search, setSearch] = useState('')

  const load = async () => {
    const { data } = await api.get('/resources/intakes', { params: { search } })
    setItems(data)
  }

  useEffect(() => { load() }, [search])

  const remove = async (id: number) => {
    await api.delete(`/resources/intakes/${id}`)
    load()
  }

  return (
    <AppShell title="Intake Database" intro="Search by name, case number, or contact person. Review the next court date, time, and location for each case.">
      <section className="panel">
        <div className="toolbar">
          <label className="toolbar-search">Search bar
            <input placeholder="Search cases" value={search} onChange={e => setSearch(e.target.value)} />
          </label>
          <Link className="button-link" to="/intakes/new">Add Intake</Link>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Case number</th>
              <th>Next court date</th>
              <th>Time</th>
              <th>Location</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.case_numbers || '—'}</td>
                <td>{item.next_court_date || '—'}</td>
                <td>{item.next_court_time || '—'}</td>
                <td>{item.court_site || item.court_location || '—'}</td>
                <td className="table-actions">
                  <Link className="button-link button-link--ghost" to={`/intakes/${item.id}`}>Details</Link>
                  {user?.role === 'admin' && <button onClick={() => remove(item.id)}>Delete</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </AppShell>
  )
}
