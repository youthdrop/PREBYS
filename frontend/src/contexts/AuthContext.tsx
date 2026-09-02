import { createContext, useEffect, useMemo, useState } from 'react'

type User = { email: string; full_name?: string; role: string } | null

type AuthContextType = {
  token: string | null
  user: User
  setSession: (token: string, user: NonNullable<User>) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  setSession: () => {},
  logout: () => {}
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('free_sd_token'))
  const [user, setUser] = useState<User>(JSON.parse(localStorage.getItem('free_sd_user') || 'null'))

  const setSession = (newToken: string, newUser: NonNullable<User>) => {
    localStorage.setItem('free_sd_token', newToken)
    localStorage.setItem('free_sd_user', JSON.stringify(newUser))
    setToken(newToken)
    setUser(newUser)
  }

  const logout = () => {
    localStorage.removeItem('free_sd_token')
    localStorage.removeItem('free_sd_user')
    setToken(null)
    setUser(null)
  }

  const value = useMemo(() => ({ token, user, setSession, logout }), [token, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
