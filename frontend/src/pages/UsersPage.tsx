import { useEffect, useState } from 'react'
import api from '../api/client'
import AppShell from '../layouts/AppShell'

const roles = ['staff', 'admin', 'volunteer']

const emptyForm = {
  email: '',
  full_name: '',
  password: '',
  role: 'staff',
  phone: '',
  is_active: true,
}

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [form, setForm] = useState<any>(emptyForm)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [message, setMessage] = useState('')

  const loadUsers = async () => {
    const res = await api.get('/users')
    setUsers(res.data || [])
  }

  useEffect(() => {
    loadUsers()
  }, [])

  const updateField = (key: string, value: any) => {
    setForm((prev: any) => ({ ...prev, [key]: value }))
  }

  const resetForm = () => {
    setForm(emptyForm)
    setEditingId(null)
    setMessage('')
  }

  const editUser = (user: any) => {
    setEditingId(user.id)
    setForm({
      email: user.email || '',
      full_name: user.full_name || '',
      password: '',
      role: user.role || 'staff',
      phone: user.phone || '',
      is_active: user.is_active,
    })
    setMessage('Leave password blank unless you want to reset it.')
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()

    const payload: any = {
      email: form.email,
      full_name: form.full_name || null,
      role: form.role,
      phone: form.phone || null,
      is_active: form.is_active,
    }

    if (form.password) {
      payload.password = form.password
    }

    if (editingId) {
      await api.put(`/users/${editingId}`, payload)
      setMessage('User updated.')
    } else {
      if (!form.password) {
        setMessage('Password is required for a new user.')
        return
      }
      await api.post('/users', payload)
      setMessage('User created.')
    }

    resetForm()
    await loadUsers()
  }

  const deactivateUser = async (user: any) => {
    await api.put(`/users/${user.id}`, {
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      phone: user.phone,
      is_active: false,
    })
    await loadUsers()
  }

  return (
    <AppShell title="Users" intro="Add staff accounts, reset passwords, and deactivate access.">
      <section className="panel form-grid">
        <h2 className="full-span">{editingId ? 'Edit user' : 'Add user'}</h2>

        {message && <p className="full-span">{message}</p>}

        <form className="full-span form-grid" onSubmit={submit}>
          <label>
            Full name
            <input value={form.full_name} onChange={e => updateField('full_name', e.target.value)} />
          </label>

          <label>
            Email
            <input type="email" value={form.email} onChange={e => updateField('email', e.target.value)} required />
          </label>

          <label>
            Temporary password
            <input
              type="text"
              value={form.password}
              onChange={e => updateField('password', e.target.value)}
              placeholder={editingId ? 'Leave blank to keep current password' : 'Required for new user'}
            />
          </label>

          <label>
            Role
            <select value={form.role} onChange={e => updateField('role', e.target.value)}>
              {roles.map(role => <option key={role} value={role}>{role}</option>)}
            </select>
          </label>

          <label>
            Phone
            <input value={form.phone} onChange={e => updateField('phone', e.target.value)} />
          </label>

          <label>
            Active
            <select value={String(form.is_active)} onChange={e => updateField('is_active', e.target.value === 'true')}>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </label>

          <div className="full-span form-actions">
            <button type="submit">{editingId ? 'Save user' : 'Create user'}</button>
            {editingId && <button type="button" onClick={resetForm}>Cancel edit</button>}
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>Staff users</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id}>
                  <td>{user.full_name || 'N/A'}</td>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>{user.is_active ? 'Active' : 'Inactive'}</td>
                  <td>
                    <button type="button" onClick={() => editUser(user)}>Edit</button>
                    {user.is_active && <button type="button" onClick={() => deactivateUser(user)}>Deactivate</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  )
}
