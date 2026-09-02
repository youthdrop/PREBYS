import { FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const emptyNote = { note_type: 'General case note', contact_method: 'In person', note: '', next_action: '', next_contact_date: '', confidential: false }

function displayDate(value?: string | null) {
  if (!value) return '—'
  return new Date(`${value}T12:00:00`).toLocaleDateString()
}

export default function YouthDetailsPage() {
  const { id } = useParams()
  const [youth, setYouth] = useState<any>()
  const [edit, setEdit] = useState<any>()
  const [staff, setStaff] = useState<any[]>([])
  const [notes, setNotes] = useState<any[]>([])
  const [documents, setDocuments] = useState<any[]>([])
  const [note, setNote] = useState<any>(emptyNote)
  const [file, setFile] = useState<File | null>(null)
  const [documentType, setDocumentType] = useState('employment_verification')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const load = async () => {
    const [profile, caseNotes, docs, staffList] = await Promise.all([
      api.get(`/mis/youth/${id}`), api.get(`/mis/youth/${id}/notes`),
      api.get(`/mis/youth/${id}/documents`), api.get('/mis/staff'),
    ])
    setYouth(profile.data); setEdit(profile.data); setNotes(caseNotes.data); setDocuments(docs.data); setStaff(staffList.data)
  }

  useEffect(() => { load().catch(() => setError('The youth profile could not be loaded.')) }, [id])

  const updateProfile = async (event: FormEvent) => {
    event.preventDefault(); setMessage(''); setError('')
    try {
      const response = await api.put(`/mis/youth/${id}`, {
        ...edit,
        assigned_staff_id: edit.assigned_staff_id ? Number(edit.assigned_staff_id) : null,
        birthdate: edit.birthdate || null,
        enrollment_date: edit.enrollment_date || null,
        next_contact_date: edit.next_contact_date || null,
      })
      setYouth(response.data); setEdit(response.data); setMessage('Youth profile updated.')
    } catch (err: any) { setError(err?.response?.data?.detail || 'The youth profile could not be updated.') }
  }

  const addNote = async (event: FormEvent) => {
    event.preventDefault(); setMessage(''); setError('')
    try {
      await api.post(`/mis/youth/${id}/notes`, note)
      setNote(emptyNote); await load(); setMessage('Case note added.')
    } catch (err: any) { setError(err?.response?.data?.detail || 'The case note could not be added.') }
  }

  const upload = async (event: FormEvent) => {
    event.preventDefault(); if (!file) return
    const formData = new FormData(); formData.append('document_type', documentType); formData.append('file', file)
    try {
      await api.post(`/mis/youth/${id}/documents`, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      setFile(null); await load(); setMessage('Verification document uploaded.')
    } catch (err: any) { setError(err?.response?.data?.detail || 'The document could not be uploaded.') }
  }

  const download = async (doc: any) => {
    const response = await api.get(`/mis/documents/${doc.id}/download`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data); const anchor = document.createElement('a')
    anchor.href = url; anchor.download = doc.original_filename; anchor.click(); URL.revokeObjectURL(url)
  }

  if (!youth || !edit) return <AppShell title="Youth Profile"><div className="panel">Loading youth profile…</div></AppShell>

  return <AppShell title={youth.name} intro={`Age ${youth.age ?? 'not available'} · ${youth.status} · Assigned to ${youth.assigned_staff_name || 'no staff member'}`}>
    {message && <div className="status" style={{ marginBottom: '1rem' }}>{message}</div>}
    {error && <div className="status status--error" style={{ marginBottom: '1rem' }}>{error}</div>}

    <div className="profile-summary">
      <div><span>Telephone</span><strong>{youth.telephone || '—'}</strong></div>
      <div><span>Email</span><strong>{youth.email || '—'}</strong></div>
      <div><span>Next contact</span><strong>{displayDate(youth.next_contact_date)}</strong></div>
      <div><span>Assigned staff</span><strong>{youth.assigned_staff_name || 'Unassigned'}</strong></div>
    </div>

    <section className="panel" style={{ marginBottom: '1rem' }}>
      <div className="section-title-row"><div><p className="eyebrow">Youth overview</p><h2>Profile and Staff Assignment</h2></div><Link className="button-link button-link--ghost" to="/youth">Back to directory</Link></div>
      <form className="form-grid" onSubmit={updateProfile}>
        <label className="full-span">Full name<input required value={edit.name || ''} onChange={(e) => setEdit({ ...edit, name: e.target.value })} /></label>
        <label>Telephone<input value={edit.telephone || ''} onChange={(e) => setEdit({ ...edit, telephone: e.target.value })} /></label>
        <label>Email<input type="email" value={edit.email || ''} onChange={(e) => setEdit({ ...edit, email: e.target.value })} /></label>
        <label>Birthdate<input type="date" value={edit.birthdate || ''} onChange={(e) => setEdit({ ...edit, birthdate: e.target.value })} /></label>
        <label>Gender<input value={edit.gender || ''} onChange={(e) => setEdit({ ...edit, gender: e.target.value })} /></label>
        <label>Race / ethnicity<input value={edit.race || ''} onChange={(e) => setEdit({ ...edit, race: e.target.value })} /></label>
        <label>Enrollment date<input type="date" value={edit.enrollment_date || ''} onChange={(e) => setEdit({ ...edit, enrollment_date: e.target.value })} /></label>
        <label>Status<select value={edit.status || 'active'} onChange={(e) => setEdit({ ...edit, status: e.target.value })}><option value="active">Active</option><option value="inactive">Inactive</option><option value="completed">Completed</option><option value="waitlist">Waitlist</option></select></label>
        <label>Assigned staff<select value={edit.assigned_staff_id || ''} onChange={(e) => setEdit({ ...edit, assigned_staff_id: e.target.value })}><option value="">Unassigned</option>{staff.map((person) => <option key={person.id} value={person.id}>{person.full_name || person.email} · {person.role}</option>)}</select></label>
        <label>Next contact date<input type="date" value={edit.next_contact_date || ''} onChange={(e) => setEdit({ ...edit, next_contact_date: e.target.value })} /></label>
        <label>Emergency contact<input value={edit.emergency_contact_name || ''} onChange={(e) => setEdit({ ...edit, emergency_contact_name: e.target.value })} /></label>
        <label>Emergency telephone<input value={edit.emergency_contact_phone || ''} onChange={(e) => setEdit({ ...edit, emergency_contact_phone: e.target.value })} /></label>
        <div className="full-span"><button>Save profile changes</button></div>
      </form>
    </section>

    <section className="profile-columns">
      <div className="panel">
        <p className="eyebrow">Ongoing documentation</p><h2 style={{ marginBottom: '1rem' }}>Add Rolling Case Note</h2>
        <form className="form-grid" onSubmit={addNote}>
          <label>Note type<select value={note.note_type} onChange={(e) => setNote({ ...note, note_type: e.target.value })}><option>General case note</option><option>Phone contact</option><option>In-person meeting</option><option>Parent / guardian contact</option><option>Outreach attempt</option><option>Employment update</option><option>Education update</option><option>Goal progress</option><option>Incident</option></select></label>
          <label>Contact method<select value={note.contact_method} onChange={(e) => setNote({ ...note, contact_method: e.target.value })}><option>In person</option><option>Telephone</option><option>Text message</option><option>Email</option><option>Video call</option><option>No direct contact</option></select></label>
          <label>Next contact<input type="date" value={note.next_contact_date} onChange={(e) => setNote({ ...note, next_contact_date: e.target.value })} /></label>
          <label className="check-label"><input type="checkbox" checked={note.confidential} onChange={(e) => setNote({ ...note, confidential: e.target.checked })} /> Confidential note</label>
          <label className="full-span">Case note<textarea required rows={5} value={note.note} onChange={(e) => setNote({ ...note, note: e.target.value })} /></label>
          <label className="full-span">Next action<textarea rows={2} value={note.next_action} onChange={(e) => setNote({ ...note, next_action: e.target.value })} /></label>
          <div className="full-span"><button>Add case note</button></div>
        </form>
      </div>

      <div className="panel">
        <p className="eyebrow">Case timeline</p><h2 style={{ marginBottom: '1rem' }}>Rolling Case Notes</h2>
        <div className="timeline">{notes.length === 0 ? <p className="muted">No case notes have been added.</p> : notes.map((item) => <article className="timeline-note" key={item.id}>
          <div className="timeline-dot" /><div><div className="note-heading"><strong>{item.note_type || 'Case note'}</strong><span>{item.contact_method || 'Contact method not listed'}</span></div><p>{item.note}</p>{item.next_action && <p><b>Next action:</b> {item.next_action}</p>}<small>{item.created_by_name || 'Staff'} · {new Date(item.created_at).toLocaleString()}{item.confidential ? ' · Confidential' : ''}</small></div>
        </article>)}</div>
      </div>
    </section>

    <section className="panel" style={{ marginTop: '1rem' }}>
      <p className="eyebrow">Document center</p><h2>Employment and School Verification</h2>
      <p className="muted" style={{ margin: '.5rem 0 1rem' }}>Allowed files: PDF, JPG, PNG, WEBP, or DOCX. Maximum file size is 10 MB.</p>
      <form className="form-grid" onSubmit={upload}>
        <label>Document type<select value={documentType} onChange={(e) => setDocumentType(e.target.value)}><option value="employment_verification">Employment verification</option><option value="school_verification">School verification</option></select></label>
        <label>File<input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp,.docx" onChange={(e) => setFile(e.target.files?.[0] || null)} /></label>
        <div className="full-span"><button disabled={!file}>Upload document</button></div>
      </form>
      <div className="document-list">{documents.map((doc) => <div className="document-row" key={doc.id}><div><span>{doc.document_type.replaceAll('_', ' ')}</span><strong>{doc.original_filename}</strong><small>Uploaded {new Date(doc.uploaded_at).toLocaleString()}</small></div><button onClick={() => download(doc)}>Download</button></div>)}</div>
    </section>
  </AppShell>
}
