import {
  createContext,
  ReactNode,
  useMemo,
  useState,
} from 'react'

export type User = {
  email: string
  full_name?: string
  role?: string
} | null

export type AuthContextType = {
  token: string | null
  user: User
  setSession: (
    token: string,
    user: NonNullable<User>
  ) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  setSession: () => {},
  logout: () => {},
})

export function AuthProvider({
  children,
}: {
  children: ReactNode
}) {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('prebys_token')
  )

  const [user, setUser] = useState<User>(() => {
    const storedUser = localStorage.getItem('prebys_user')

    if (!storedUser) {
      return null
    }

    try {
      return JSON.parse(storedUser)
    } catch {
      localStorage.removeItem('prebys_user')
      return null
    }
  })

  const setSession = (
    newToken: string,
    newUser: NonNullable<User>
  ) => {
    localStorage.setItem('prebys_token', newToken)
    localStorage.setItem(
      'prebys_user',
      JSON.stringify(newUser)
    )

    setToken(newToken)
    setUser(newUser)
  }

  const logout = () => {
    localStorage.removeItem('prebys_token')
    localStorage.removeItem('prebys_user')

    setToken(null)
    setUser(null)
  }

  const value = useMemo<AuthContextType>(
    () => ({
      token,
      user,
      setSession,
      logout,
    }),
    [token, user]
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
