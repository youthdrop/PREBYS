import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'
import { useAuth } from '../hooks/useAuth'

const labels: Record<string, { title: string; addLabel: string; intro: string }> = {
  attorneys: { title: 'Attorney Database', addLabel: 'Add Attorney', intro: 'Search attorneys, review contact details, and see how many cases are linked to each attorney.' },
  judges: { title: 'Judge Database', addLabel: 'Add Judge', intro: 'Search judges, clerk phone numbers, courtrooms, and case volume.' },
  prosecutors: { title: 'DA / Prosecutor Database', addLabel: 'Add DA', intro: 'Search district attorneys and prosecutors linked to case records.' },
  volunteers: { title: 'Volunteer Database', addLabel: 'Add Volunteer', intro: 'Review volunteer availability, travel courts, training, and notes.' },
}

export default function EntityListPage({ entity }: { entity: string }) {
  const { user } = useAuth()
  const navigate = useNavigate()

  const [items, setItems] = useState<any[]>([])
  const [search, setSearch] = useState('')

  const load = async () => {
    const { data } = await api.get(`/resources/${entity}`, { params: { search } })
    setItems(data)
  }

  useEffect(() => {
    load()
  }, [search, entity])

  const remove = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return
    await api.delete(`/resources/${entity}/${id}`)
    load()
  }

  const meta = labels[entity]

  return (
    <AppShell title={meta.title} intro={meta.intro}>
      <section className="panel">
        <div className="toolbar">
          <label className="toolbar-search">
            Search
            <input
              placeholder={`Search ${meta.title.toLowerCase()}`}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </label>

          <Link className="button-link" to={`/${entity}/new`}>
            {meta.addLabel}
          </Link>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Contact</th>
              <th>Additional info</th>
              <th>Cases</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                
                {/* 🔥 CLICK NAME TO EDIT */}
                <td
                  style={{ cursor: 'pointer', fontWeight: 'bold' }}
                  onClick={() => navigate(`/${entity}/${item.id}`)}
                >
                  {item.name}
                </td>

                <td>
                  <div>{item.email || '—'}</div>
                  <div>{item.telephone || item.clerk_telephone || '—'}</div>
                </td>

                <td>
                  {item.business_name ||
                    item.courtroom ||
                    item.training_type ||
                    item.travel_courts ||
                    '—'}
                </td>

                <td>{item.case_count || 0}</td>

                <td style={{ display: 'flex', gap: 8 }}>
                  
                  {/* ✅ EDIT BUTTON */}
                  <button onClick={() => navigate(`/${entity}/${item.id}`)}>
                    Edit
                  </button>

                  {/* ✅ DELETE BUTTON */}
                  {user?.role === 'admin' && (
                    <button onClick={() => remove(item.id)}>
                      Delete
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </AppShell>
  )
}