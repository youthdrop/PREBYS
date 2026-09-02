import { useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import api from '../api/client'
import BrandMark from '../components/BrandMark'

export default function ResetPasswordPage() {
  const location = useLocation()
  const token = useMemo(() => new URLSearchParams(location.search).get('token') || '', [location.search])
  const [newPassword, setNewPassword] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/reset-password', { token, new_password: newPassword })
      setMessage(data.message)
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Unable to reset password.')
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <BrandMark subtitle="Create a new password" />
        <h1>Reset password</h1>
        <label>New password
          <input type="password" placeholder="New password" value={newPassword} onChange={e => setNewPassword(e.target.value)} />
        </label>
        <button type="submit">Save new password</button>
        {message && <div className="status">{message}</div>}
        {error && <div className="status status--error">{error}</div>}
        <div className="auth-links"><Link to="/login">Back to login</Link></div>
      </form>
    </div>
  )
}
