import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'https://freesd2-production.up.railway.app'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('free_sd_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export async function loginRequest(email: string, password: string) {
  const response = await api.post('/auth/login', {
    email: email.trim(),
    password,
    delivery_method: 'email',
  })
  return response.data
}

export async function verifyOtpRequest(email: string, code: string) {
  const response = await api.post('/auth/verify-otp', {
    email: email.trim(),
    code: code.trim(),
  })
  return response.data
}

export async function forgotPasswordRequest(email: string) {
  const response = await api.post('/auth/forgot-password', {
    email: email.trim(),
    delivery_method: 'email',
  })
  return response.data
}

export async function resetPasswordRequest(token: string, newPassword: string) {
  const response = await api.post('/auth/reset-password', {
    token,
    new_password: newPassword,
  })
  return response.data
}