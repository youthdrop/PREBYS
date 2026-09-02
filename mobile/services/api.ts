const API_URL = 'http://192.168.1.168:8000'

function buildUrl(path: string) {
  return `${API_URL}${path.startsWith('/') ? path : `/${path}`}`
}

export async function postJson(path: string, payload: any) {
  const url = buildUrl(path)

  console.log('API CALL →', url)

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const text = await res.text()

  let data: any = {}
  try {
    data = text ? JSON.parse(text) : {}
  } catch {
    data = { raw: text }
  }

  if (!res.ok) {
    throw new Error(data.detail || data.message || `Request failed (${res.status})`)
  }

  return data
}

export async function login(email: string, password: string) {
  return postJson('/auth/login', {
    email: email.trim(),
    password,
    delivery_method: 'email',
  })
}

export async function verifyOtp(email: string, code: string) {
  return postJson('/auth/verify-otp', {
    email: email.trim(),
    code: code.trim(),
  })
}

export async function forgotPassword(email: string) {
  return postJson('/auth/forgot-password', {
    email: email.trim(),
    delivery_method: 'email',
  })
}

export async function resetPassword(token: string, newPassword: string) {
  return postJson('/auth/reset-password', {
    token,
    new_password: newPassword,
  })
}