import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import BrandMark from '../components/BrandMark'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [deliveryMethod, setDeliveryMethod] = useState('email')
  const [message, setMessage] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    const { data } = await api.post('/auth/forgot-password', { email, delivery_method: deliveryMethod })
    setMessage(data.message)
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <BrandMark subtitle="Password recovery" />
        <h1>Forgot password</h1>
        <label>Email
          <input placeholder="you@example.org" value={email} onChange={e => setEmail(e.target.value)} />
        </label>
        <label>Send reset link by
          <select value={deliveryMethod} onChange={e => setDeliveryMethod(e.target.value)}>
            <option value="email">Email link</option>
            <option value="text">Text link</option>
          </select>
        </label>
        <button type="submit">Send reset link</button>
        {message && <div className="status">{message}</div>}
        <div className="auth-links"><Link to="/login">Back to login</Link></div>
      </form>
    </div>
  )
}
