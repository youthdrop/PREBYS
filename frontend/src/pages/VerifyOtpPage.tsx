import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import BrandMark from '../components/BrandMark'
import { useAuth } from '../hooks/useAuth'

export default function VerifyOtpPage() {
  const navigate = useNavigate()
  const { setSession } = useAuth()
  const email = sessionStorage.getItem('otp_email') || ''
  const [code, setCode] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/auth/verify-otp', { email, code })
      setSession(data.access_token, data.user)
      navigate('/')
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid or expired verification code.')
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <BrandMark subtitle="Verification step" />
        <h1>Enter verification code</h1>
        <p className="muted">Code sent to {email || 'your account'}.</p>
        <label>6-digit code
          <input placeholder="123456" value={code} onChange={e => setCode(e.target.value)} maxLength={6} />
        </label>
        <button type="submit">Verify and continue</button>
        {error && <div className="status status--error">{error}</div>}
        <div className="auth-links">
          <Link to="/login">Back to login</Link>
        </div>
      </form>
    </div>
  )
}
