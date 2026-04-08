import { createContext, useContext, useEffect, useState, useCallback, type ReactNode } from 'react'
import { api } from '../lib/api'

interface User {
  id: string
  username: string
  email: string
  display_name: string
  role: string
}

// Backend returns permissions as Record<string, string[]>  e.g. {"chat": ["view", "execute"]}
type Permissions = Record<string, string[]>

interface AuthContextType {
  user: User | null
  loading: boolean
  permissions: Permissions
  needsSetup: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  hasPermission: (resource: string, action: string) => boolean
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [permissions, setPermissions] = useState<Permissions>({})
  const [loading, setLoading] = useState(true)
  const [needsSetup, setNeedsSetup] = useState(false)

  const refreshUser = useCallback(async () => {
    try {
      const setupRes = await api.get('/auth/needs-setup')
      if (setupRes.needs_setup) {
        setNeedsSetup(true)
        setUser(null)
        setPermissions({})
        return
      }
      setNeedsSetup(false)

      const meRes = await api.get('/auth/me')
      setUser(meRes.user)
      setPermissions(meRes.permissions || {})
    } catch {
      setUser(null)
      setPermissions({})
    }
  }, [])

  useEffect(() => {
    refreshUser().finally(() => setLoading(false))
  }, [refreshUser])

  const login = useCallback(async (username: string, password: string) => {
    const res = await api.post('/auth/login', { username, password })
    setUser(res.user)
    await refreshUser()
  }, [refreshUser])

  const logout = useCallback(async () => {
    await api.post('/auth/logout')
    setUser(null)
    setPermissions({})
  }, [])

  const hasPermission = useCallback((resource: string, action: string) => {
    if (user?.role === 'admin') return true
    const actions = permissions[resource]
    return Array.isArray(actions) && actions.includes(action)
  }, [user, permissions])

  return (
    <AuthContext.Provider
      value={{ user, loading, permissions, needsSetup, login, logout, hasPermission, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  )
}
