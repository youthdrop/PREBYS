import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const serviceTypes = ['Social bio', 'In person', 'Court', 'Meeting with attorney', 'Phone call']

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

export default function IntakeDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState<any | null>(null)
  const [notes, setNotes] = useState<any[]>([])
  const [noteForm, setNoteForm] = useState<any>({ service_type: 'Court', note_date: '', time_saved_hours: '', note: '' })
  const [lookups, setLookups] = useState<any>({
    courts: [],
    attorneys: [],
    judges: [],
    prosecutors: [],
    volunteers: [],
  })

  useEffect(() => {
    const load = async () => {
      const [lookupsRes, intakeRes, volunteersRes, notesRes] = await Promise.all([
        api.get('/resources/lookups'),
        api.get(`/resources/intakes/${id}`),
        api.get('/resources/volunteers'),
        api.get(`/resources/intakes/${id}/notes`),
      ])

      const data = intakeRes.data

      setLookups({
        ...lookupsRes.data,
        volunteers: volunteersRes.data || [],
      })

      setNotes(notesRes.data || [])

      setForm({
        ...data,
        attorney_id: data.attorney_id || '',
        judge_id: data.judge_id || '',
        prosecutor_id: data.prosecutor_id || '',
        volunteer_assigned: data.volunteer_assigned || '',
        next_court_time: data.next_court_time?.slice?.(0, 5) || data.next_court_time || '',
        hearing_type: data.hearing_type || '',
      })
    }

    load()
  }, [id])

  if (!form) {
    return (
      <AppShell title="Case Details">
        <div className="panel">Loading...</div>
      </AppShell>
    )
  }

  const updateField = (key: string, value: any) => {
    setForm((prev: any) => ({ ...prev, [key]: value }))
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()

    await api.put(`/resources/intakes/${id}`, {
      ...form,
      attorney_id: form.attorney_id ? Number(form.attorney_id) : null,
      judge_id: form.judge_id ? Number(form.judge_id) : null,
      prosecutor_id: form.prosecutor_id ? Number(form.prosecutor_id) : null,
      volunteer_assigned: form.volunteer_assigned || null,
      next_court_date: form.next_court_date || null,
      next_court_time: form.next_court_time ? `${form.next_court_time}:00` : null,
      hearing_type: form.hearing_type || null,
    })

    navigate('/intakes')
  }


  const updateNoteField = (key: string, value: any) => {
    setNoteForm((prev: any) => ({ ...prev, [key]: value }))
  }

  const addCaseNote = async (e: React.FormEvent) => {
    e.preventDefault()

    await api.post(`/resources/intakes/${id}/notes`, {
      service_type: noteForm.service_type || null,
      note_date: noteForm.note_date || null,
      time_saved_hours: noteForm.time_saved_hours ? Number(noteForm.time_saved_hours) : null,
      note: noteForm.note,
    })

    const notesRes = await api.get(`/resources/intakes/${id}/notes`)
    const intakeRes = await api.get(`/resources/intakes/${id}`)

    setNotes(notesRes.data || [])
    setForm((prev: any) => ({
      ...prev,
      ...intakeRes.data,
      attorney_id: intakeRes.data.attorney_id || '',
      judge_id: intakeRes.data.judge_id || '',
      prosecutor_id: intakeRes.data.prosecutor_id || '',
      volunteer_assigned: intakeRes.data.volunteer_assigned || '',
      next_court_time: intakeRes.data.next_court_time?.slice?.(0, 5) || intakeRes.data.next_court_time || '',
      hearing_type: intakeRes.data.hearing_type || '',
    }))
    setNoteForm({ service_type: 'Court', note_date: '', time_saved_hours: '', note: '' })
  }

  return (
    <AppShell title="Case Details" intro="Name, case number, volunteer assignment, court information, and notes can all be updated here.">
      <div className="detail-banner">
        <div><span>Name</span><strong>{form.name}</strong></div>
        <div><span>Case number</span><strong>{form.case_numbers || 'N/A'}</strong></div>
      </div>

      <form className="stack-gap" onSubmit={submit}>
        <section className="panel form-grid">
          <h2 className="full-span">Case details</h2>

          <label>
            Name
            <input
              value={form.name || ''}
              onChange={e => updateField('name', e.target.value)}
            />
          </label>

          <label>
            Case number
            <input
              value={form.case_numbers || ''}
              onChange={e => updateField('case_numbers', e.target.value)}
            />
          </label>

          <label className="full-span">
            Charges
            <textarea
              rows={3}
              value={form.charges || ''}
              onChange={e => updateField('charges', e.target.value)}
            />
          </label>

          <label>
            Contact person
            <input
              value={form.contact_person || ''}
              onChange={e => updateField('contact_person', e.target.value)}
            />
          </label>

          <label>
            Contact person telephone
            <input
              value={form.contact_person_telephone || ''}
              onChange={e => updateField('contact_person_telephone', e.target.value)}
            />
          </label>

          <label>
            Contact person email
            <input
              value={form.contact_person_email || ''}
              onChange={e => updateField('contact_person_email', e.target.value)}
            />
          </label>

          <label>
            Volunteer assigned
            <select
              value={form.volunteer_assigned || ''}
              onChange={e => updateField('volunteer_assigned', e.target.value)}
            >
              <option value="">Select volunteer</option>
              {lookups.volunteers.map((item: any) => {
                const label = item.name || item.full_name || item.email || `Volunteer ${item.id}`
                return (
                  <option key={item.id} value={label}>
                    {label}
                  </option>
                )
              })}
            </select>
          </label>

          <label>
            Maximum exposure
            <input
              value={form.maximum_exposure || ''}
              onChange={e => updateField('maximum_exposure', e.target.value)}
            />
          </label>

          <label>
            Court locations
            <input
              value={form.court_location || ''}
              onChange={e => updateField('court_location', e.target.value)}
            />
          </label>
        </section>

        <section className="panel form-grid">
          <h2 className="full-span">New court date, time, and place</h2>

          <label>
            Date
            <input
              type="date"
              value={form.next_court_date || ''}
              onChange={e => updateField('next_court_date', e.target.value)}
            />
          </label>

          <label>
            Time
            <input
              type="time"
              value={form.next_court_time || ''}
              onChange={e => updateField('next_court_time', e.target.value)}
            />
          </label>

          <label>
            Place
            <select
              value={form.court_site || ''}
              onChange={e => updateField('court_site', e.target.value)}
            >
              <option value="">Select court</option>
              {lookups.courts.map((court: string) => (
                <option key={court} value={court}>{court}</option>
              ))}
            </select>
          </label>

          <label>
            Hearing type
            <select
              value={form.hearing_type || ''}
              onChange={e => updateField('hearing_type', e.target.value)}
            >
              <option value="">Select hearing type</option>
              {hearingTypes.map((hearing) => (
                <option key={hearing} value={hearing}>{hearing}</option>
              ))}
            </select>
          </label>

          <label>
            Attorney
            <select
              value={form.attorney_id || ''}
              onChange={e => updateField('attorney_id', e.target.value)}
            >
              <option value="">Select attorney</option>
              {lookups.attorneys.map((item: any) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>

          <label>
            Judge
            <select
              value={form.judge_id || ''}
              onChange={e => updateField('judge_id', e.target.value)}
            >
              <option value="">Select judge</option>
              {lookups.judges.map((item: any) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>

          <label>
            DA / Prosecutor
            <select
              value={form.prosecutor_id || ''}
              onChange={e => updateField('prosecutor_id', e.target.value)}
            >
              <option value="">Select DA / prosecutor</option>
              {lookups.prosecutors.map((item: any) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>
        </section>

        <section className="panel">
          <div className="form-actions">
            <button type="submit">Save case details</button>
            <Link className="button-link button-link--ghost" to="/intakes">
              Return to intake database
            </Link>
          </div>
        </section>
      </form>

      <section className="panel form-grid">
        <h2 className="full-span">Add rolling case note</h2>

        <form className="full-span form-grid" onSubmit={addCaseNote}>
          <label>
            Type of service
            <select value={noteForm.service_type} onChange={e => updateNoteField('service_type', e.target.value)}>
              {serviceTypes.map(service => <option key={service} value={service}>{service}</option>)}
            </select>
          </label>

          <label>
            Date of case note
            <input type="date" value={noteForm.note_date} onChange={e => updateNoteField('note_date', e.target.value)} />
          </label>

          <label>
            Time saved
            <input type="number" step="0.25" value={noteForm.time_saved_hours} onChange={e => updateNoteField('time_saved_hours', e.target.value)} />
          </label>

          <label className="full-span">
            New note
            <textarea rows={5} value={noteForm.note} onChange={e => updateNoteField('note', e.target.value)} required />
          </label>

          <div className="full-span form-actions">
            <button type="submit">Add note to timeline</button>
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>Case note timeline</h2>
        {notes.length === 0 && <p>No case notes added yet.</p>}
        <div className="stack-gap">
          {notes.map(note => (
            <article key={note.id} className="panel">
              <p><strong>{note.note_date || note.created_at?.slice?.(0, 10)}</strong> · {note.service_type || 'Service'} · {note.time_saved_hours || 0} hours</p>
              <p>{note.note}</p>
              <p><small>Added by {note.created_by_name || note.created_by_email || 'staff'} on {note.created_at?.slice?.(0, 10)}</small></p>
            </article>
          ))}
        </div>
      </section>

    </AppShell>
  )
}