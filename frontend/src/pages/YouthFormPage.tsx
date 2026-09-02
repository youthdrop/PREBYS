import { FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const initial = {
  name: '', telephone: '', email: '', gender: '', race: '', birthdate: '',
  enrollment_date: new Date().toISOString().slice(0, 10), status: 'active',
  assigned_staff_id: '', next_contact_date: '', emergency_contact_name: '',
  emergency_contact_phone: '',
}

export default function YouthFormPage() {
  const [form, setForm] = useState<any>(initial)
  const [staff, setStaff] = useState<any[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => { api.get('/mis/staff').then((r) => setStaff(r.data)).catch(() => setStaff([])) }, [])
  const set = (key: string, value: any) => setForm((current: any) => ({ ...current, [key]: value }))

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setSaving(true); setError('')
    try {
      const response = await api.post('/mis/youth', {
        ...form,
        assigned_staff_id: form.assigned_staff_id ? Number(form.assigned_staff_id) : null,
        birthdate: form.birthdate || null,
        next_contact_date: form.next_contact_date || null,
      })
      navigate(`/youth/${response.data.id}`)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'The youth intake could not be saved.')
    } finally { setSaving(false) }
  }

  return <AppShell title="Youth Intake" intro="Create a youth profile, assign a staff member, and establish the first follow-up date. Age is calculated automatically from birthdate.">
    {error && <div className="status status--error" style={{ marginBottom: '1rem' }}>{error}</div>}
    <form className="panel form-grid" onSubmit={submit}>
      <label className="full-span">Full name<input required value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="Youth's full name" /></label>
      <label>Telephone<input value={form.telephone} onChange={(e) => set('telephone', e.target.value)} placeholder="(619) 555-0000" /></label>
      <label>Email<input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} placeholder="name@example.com" /></label>
      <label>Birthdate<input type="date" value={form.birthdate} onChange={(e) => set('birthdate', e.target.value)} /></label>
      <label>Gender<select value={form.gender} onChange={(e) => set('gender', e.target.value)}><option value="">Select</option><option>Female</option><option>Male</option><option>Nonbinary</option><option>Transgender</option><option>Questioning</option><option>Prefer not to answer</option><option>Other</option></select></label>
      <label>Race / ethnicity<select value={form.race} onChange={(e) => set('race', e.target.value)}><option value="">Select</option><option>Black / African American</option><option>Hispanic / Latino</option><option>White</option><option>Asian</option><option>Native American / Alaska Native</option><option>Native Hawaiian / Pacific Islander</option><option>Middle Eastern / North African</option><option>Multiracial</option><option>Prefer not to answer</option><option>Other</option></select></label>
      <label>Enrollment date<input type="date" value={form.enrollment_date} onChange={(e) => set('enrollment_date', e.target.value)} /></label>
      <label>Status<select value={form.status} onChange={(e) => set('status', e.target.value)}><option value="active">Active</option><option value="inactive">Inactive</option><option value="completed">Completed</option><option value="waitlist">Waitlist</option></select></label>
      <label>Assigned staff<select value={form.assigned_staff_id} onChange={(e) => set('assigned_staff_id', e.target.value)}><option value="">Unassigned</option>{staff.map((person) => <option key={person.id} value={person.id}>{person.full_name || person.email} · {person.role}</option>)}</select></label>
      <label>Next contact date<input type="date" value={form.next_contact_date} onChange={(e) => set('next_contact_date', e.target.value)} /></label>
      <label>Emergency contact name<input value={form.emergency_contact_name} onChange={(e) => set('emergency_contact_name', e.target.value)} /></label>
      <label>Emergency contact telephone<input value={form.emergency_contact_phone} onChange={(e) => set('emergency_contact_phone', e.target.value)} /></label>
      <div className="full-span form-actions"><button disabled={saving}>{saving ? 'Saving…' : 'Create youth profile'}</button><Link className="button-link button-link--ghost" to="/youth">Cancel</Link></div>
    </form>
  </AppShell>
}
