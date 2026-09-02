import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const empty = {
  name: '',
  case_numbers: '',
  charges: '',
  contact_person: '',
  contact_person_telephone: '',
  contact_person_email: '',
  volunteer_assigned: '',
  maximum_exposure: '',
  court_location: '',
  next_court_date: '',
  next_court_time: '',
  court_site: 'Central',
  hearing_type: '',
  attorney_id: '',
  judge_id: '',
  prosecutor_id: '',
  attorney: {
    name: '',
    business_name: '',
    email: '',
    telephone: '',
  },
  judge: {
    name: '',
    clerk_telephone: '',
    courtroom: '',
  },
  prosecutor: {
    name: '',
    email: '',
    telephone: '',
  },
}

const hearingTypes = [
  'Arraignment',
  'Bail Motion',
  'Other Motion',
  'Further Proceedings',
  'Preliminary Hearing',
  'Trial',
  'Jury Selection',
  'Resentencing Hearing',
  'SB 1437 Hearing',
]

export default function IntakeFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<any>(empty)
  const [lookups, setLookups] = useState<any>({
    courts: ['Central', 'Southbay', 'El Cajon', 'Vista', 'Juvenile Court'],
    attorneys: [],
    judges: [],
    prosecutors: [],
    volunteers: [],
  })
  const [showNewAttorney, setShowNewAttorney] = useState(false)
  const [showNewJudge, setShowNewJudge] = useState(false)
  const [showNewProsecutor, setShowNewProsecutor] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadLookups = async () => {
      try {
        const { data } = await api.get('/resources/lookups')
        setLookups({
          courts: data?.courts?.length ? data.courts : ['Central', 'Southbay', 'El Cajon', 'Vista', 'Juvenile Court'],
          attorneys: data?.attorneys || [],
          judges: data?.judges || [],
          prosecutors: data?.prosecutors || [],
          volunteers: data?.volunteers || [],
        })
      } catch (err: any) {
        console.error('ERROR LOADING LOOKUPS:', err.response?.data || err.message)
      }
    }

    loadLookups()
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      setLoading(true)

      const payload = {
        ...form,
        next_court_date: form.next_court_date || null,
        next_court_time: form.next_court_time ? `${form.next_court_time}:00` : null,
        attorney_id: form.attorney_id ? Number(form.attorney_id) : null,
        judge_id: form.judge_id ? Number(form.judge_id) : null,
        prosecutor_id: form.prosecutor_id ? Number(form.prosecutor_id) : null,
        attorney: showNewAttorney && form.attorney?.name?.trim()
          ? {
              name: form.attorney.name.trim(),
              business_name: form.attorney.business_name?.trim() || null,
              email: form.attorney.email?.trim() || null,
              telephone: form.attorney.telephone?.trim() || null,
            }
          : null,
        judge: showNewJudge && form.judge?.name?.trim()
          ? {
              name: form.judge.name.trim(),
              clerk_telephone: form.judge.clerk_telephone?.trim() || null,
              courtroom: form.judge.courtroom?.trim() || null,
            }
          : null,
        prosecutor: showNewProsecutor && form.prosecutor?.name?.trim()
          ? {
              name: form.prosecutor.name.trim(),
              email: form.prosecutor.email?.trim() || null,
              telephone: form.prosecutor.telephone?.trim() || null,
            }
          : null,
      }

      console.log('SENDING PAYLOAD:', payload)

      const res = await api.post('/resources/intakes', payload)

      console.log('SUCCESS:', res.data)

      navigate('/intakes')
    } catch (err: any) {
      console.error('ERROR SAVING INTAKE:', err.response?.data || err.message)

      alert(
        typeof err.response?.data?.detail === 'string'
          ? err.response.data.detail
          : JSON.stringify(err.response?.data || { message: 'Failed to save intake' }, null, 2)
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <AppShell title="Add Intake" intro="Create a new intake and assign court relationships. Rolling case notes are added from the case details page.">
      <form className="stack-gap" onSubmit={submit}>
        <section className="panel form-grid">
          <h2 className="full-span">Case intake</h2>

          <label>
            Name
            <input
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>

          <label>
            Case numbers
            <input
              value={form.case_numbers}
              onChange={e => setForm({ ...form, case_numbers: e.target.value })}
            />
          </label>

          <label className="full-span">
            Charges
            <textarea
              rows={3}
              value={form.charges}
              onChange={e => setForm({ ...form, charges: e.target.value })}
            />
          </label>

          <label>
            Contact person
            <input
              value={form.contact_person}
              onChange={e => setForm({ ...form, contact_person: e.target.value })}
            />
          </label>

          <label>
            Contact person telephone
            <input
              value={form.contact_person_telephone}
              onChange={e => setForm({ ...form, contact_person_telephone: e.target.value })}
            />
          </label>

          <label>
            Contact person email
            <input
              type="email"
              value={form.contact_person_email}
              onChange={e => setForm({ ...form, contact_person_email: e.target.value })}
            />
          </label>

          <label>
            Volunteer assigned
            <input
              value={form.volunteer_assigned}
              onChange={e => setForm({ ...form, volunteer_assigned: e.target.value })}
            />
          </label>

          <label>
            Maximum exposure
            <input
              value={form.maximum_exposure}
              onChange={e => setForm({ ...form, maximum_exposure: e.target.value })}
            />
          </label>

          <label>
            Court location
            <input
              value={form.court_location}
              onChange={e => setForm({ ...form, court_location: e.target.value })}
            />
          </label>

          <label>
            Next court date
            <input
              type="date"
              value={form.next_court_date}
              onChange={e => setForm({ ...form, next_court_date: e.target.value })}
            />
          </label>

          <label>
            Time
            <input
              type="time"
              value={form.next_court_time}
              onChange={e => setForm({ ...form, next_court_time: e.target.value })}
            />
          </label>

          <label>
            Select court
            <select
              value={form.court_site}
              onChange={e => setForm({ ...form, court_site: e.target.value })}
            >
              {(lookups.courts || []).map((court: string) => (
                <option key={court} value={court}>
                  {court}
                </option>
              ))}
            </select>
          </label>

          <label>
            Hearing type
            <select
              value={form.hearing_type || ''}
              onChange={e => setForm({ ...form, hearing_type: e.target.value })}
            >
              <option value="">Select hearing type</option>
              {hearingTypes.map((hearing) => (
                <option key={hearing} value={hearing}>
                  {hearing}
                </option>
              ))}
            </select>
          </label>
        </section>

        <section className="panel form-grid">
          <h2 className="full-span">Court team</h2>

          <label>
            Attorney
            <select
              value={form.attorney_id}
              onChange={e => setForm({ ...form, attorney_id: e.target.value })}
            >
              <option value="">Select existing attorney</option>
              {(lookups.attorneys || []).map((item: any) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label className="check-label">
            <input
              type="checkbox"
              checked={showNewAttorney}
              onChange={e => setShowNewAttorney(e.target.checked)}
            />{' '}
            Add new attorney
          </label>

          {showNewAttorney && (
            <>
              <label>
                Attorney name
                <input
                  value={form.attorney?.name || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      attorney: { ...form.attorney, name: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Business name
                <input
                  value={form.attorney?.business_name || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      attorney: { ...form.attorney, business_name: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Email
                <input
                  type="email"
                  value={form.attorney?.email || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      attorney: { ...form.attorney, email: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Telephone
                <input
                  value={form.attorney?.telephone || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      attorney: { ...form.attorney, telephone: e.target.value },
                    })
                  }
                />
              </label>
            </>
          )}

          <label>
            Judge
            <select
              value={form.judge_id}
              onChange={e => setForm({ ...form, judge_id: e.target.value })}
            >
              <option value="">Select existing judge</option>
              {(lookups.judges || []).map((item: any) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label className="check-label">
            <input
              type="checkbox"
              checked={showNewJudge}
              onChange={e => setShowNewJudge(e.target.checked)}
            />{' '}
            Add new judge
          </label>

          {showNewJudge && (
            <>
              <label>
                Judge name
                <input
                  value={form.judge?.name || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      judge: { ...form.judge, name: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Clerk telephone number
                <input
                  value={form.judge?.clerk_telephone || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      judge: { ...form.judge, clerk_telephone: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Courtroom
                <input
                  value={form.judge?.courtroom || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      judge: { ...form.judge, courtroom: e.target.value },
                    })
                  }
                />
              </label>
            </>
          )}

          <label>
            DA / Prosecutor
            <select
              value={form.prosecutor_id}
              onChange={e => setForm({ ...form, prosecutor_id: e.target.value })}
            >
              <option value="">Select existing DA / prosecutor</option>
              {(lookups.prosecutors || []).map((item: any) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label className="check-label">
            <input
              type="checkbox"
              checked={showNewProsecutor}
              onChange={e => setShowNewProsecutor(e.target.checked)}
            />{' '}
            Add new DA / prosecutor
          </label>

          {showNewProsecutor && (
            <>
              <label>
                DA / prosecutor name
                <input
                  value={form.prosecutor?.name || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      prosecutor: { ...form.prosecutor, name: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Email
                <input
                  type="email"
                  value={form.prosecutor?.email || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      prosecutor: { ...form.prosecutor, email: e.target.value },
                    })
                  }
                />
              </label>

              <label>
                Telephone
                <input
                  value={form.prosecutor?.telephone || ''}
                  onChange={e =>
                    setForm({
                      ...form,
                      prosecutor: { ...form.prosecutor, telephone: e.target.value },
                    })
                  }
                />
              </label>
            </>
          )}
        </section>

        <section className="panel">
          <div className="form-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save intake'}
            </button>
          </div>
        </section>
      </form>
    </AppShell>
  )
}