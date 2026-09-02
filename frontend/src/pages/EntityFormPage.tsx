import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const config: Record<string, { title: string; intro: string; fields: Array<{ key: string; label: string; type?: string; placeholder?: string }> }> = {
  attorneys: {
    title: 'Add Attorney',
    intro: 'Record attorney contact information, business details, and case notes.',
    fields: [
      { key: 'name', label: 'Attorney name' },
      { key: 'business_name', label: 'Business name' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'telephone', label: 'Telephone' },
      { key: 'notes', label: 'Case note', type: 'textarea' },
      { key: 'note_date', label: 'Date of notes', type: 'date' },
    ],
  },
  judges: {
    title: 'Add Judge',
    intro: 'Record the judge, courtroom, clerk telephone, and case notes.',
    fields: [
      { key: 'name', label: 'Judge name' },
      { key: 'clerk_telephone', label: 'Clerk telephone number' },
      { key: 'courtroom', label: 'Courtroom' },
      { key: 'notes', label: 'Case note', type: 'textarea' },
      { key: 'note_date', label: 'Date of notes', type: 'date' },
    ],
  },
  prosecutors: {
    title: 'Add DA / Prosecutor',
    intro: 'Record district attorney or prosecutor contact details and notes.',
    fields: [
      { key: 'name', label: 'DA / prosecutor name' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'telephone', label: 'Telephone' },
      { key: 'notes', label: 'Case note', type: 'textarea' },
      { key: 'note_date', label: 'Date of notes', type: 'date' },
    ],
  },
  volunteers: {
    title: 'Add Volunteer',
    intro: 'Track volunteer contact information, availability, travel courts, training, and notes.',
    fields: [
      { key: 'name', label: 'Name' },
      { key: 'email', label: 'Email', type: 'email' },
      { key: 'telephone', label: 'Telephone' },
      { key: 'availability', label: 'Days and times available', type: 'textarea' },
      { key: 'travel_courts', label: 'Courts they can travel to', placeholder: 'Central, El Cajon, Vista, Southbay' },
      { key: 'training_completed_date', label: 'Date completed training', type: 'date' },
      { key: 'training_type', label: 'Type of training', placeholder: 'court watcher, social bio, other' },
      { key: 'notes', label: 'Case notes', type: 'textarea' },
    ],
  },
}

export default function EntityFormPage({ entity }: { entity: string }) {
  const navigate = useNavigate()
  const screen = config[entity]
  const initial = useMemo(() => Object.fromEntries(screen.fields.map((field) => [field.key, ''])), [screen.fields])
  const [form, setForm] = useState<Record<string, string>>(initial)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    await api.post(`/resources/${entity}`, form)
    navigate(`/${entity}`)
  }

  return (
    <AppShell title={screen.title} intro={screen.intro}>
      <form className="panel form-grid" onSubmit={submit}>
        {screen.fields.map((field) => (
          <label key={field.key} className={field.type === 'textarea' ? 'full-span' : ''}>
            {field.label}
            {field.type === 'textarea' ? (
              <textarea rows={4} placeholder={field.placeholder} value={form[field.key]} onChange={e => setForm({ ...form, [field.key]: e.target.value })} />
            ) : (
              <input type={field.type || 'text'} placeholder={field.placeholder} value={form[field.key]} onChange={e => setForm({ ...form, [field.key]: e.target.value })} />
            )}
          </label>
        ))}
        <div className="full-span form-actions">
          <button type="submit">Save record</button>
        </div>
      </form>
    </AppShell>
  )
}
