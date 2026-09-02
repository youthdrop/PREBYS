import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import BrandMark from '../components/BrandMark'

export default function LoginPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '', delivery_method: 'email' })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/login', form)
      setMessage(data.message)
      sessionStorage.setItem('otp_email', form.email)
      navigate('/verify-otp')
    } catch (err: any) {
      console.log("LOGIN ERROR:", err)
      console.log("BACKEND ERROR:", err?.response?.data)

      setError(
        err?.response?.data?.detail ||
        err?.message ||
        'Unable to send verification code.'
    )
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <BrandMark subtitle="Secure login with two-step authentication" />
        <div className="auth-grid">
          <label>Email
            <input placeholder="you@example.org" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
          </label>
          <label>Password
            <input type="password" placeholder="Password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
          </label>
          <label>Send verification code by
            <select value={form.delivery_method} onChange={e => setForm({ ...form, delivery_method: e.target.value })}>
              <option value="email">Email code</option>
              <option value="text">Text code</option>
            </select>
          </label>
        </div>
        <button type="submit">Send verification code</button>
        {message && <div className="status">{message}</div>}
        {error && <div className="status status--error">{error}</div>}
        <div className="auth-links">
          <Link to="/forgot-password">Forgot password?</Link>
        </div>
      </form>
    </div>
  )
}
