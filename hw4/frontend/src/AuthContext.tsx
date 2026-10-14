import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { fetchCurrentUser, postLogin, postLogout, postSignup } from './api'
import type { PublicUser, SignupInput } from './types'

type AuthState = {
  user: PublicUser | null
  /** True until the first /api/auth/me call settles, so the nav can avoid flickering. */
  loading: boolean
  logIn: (email: string, password: string) => Promise<void>
  signUp: (input: SignupInput) => Promise<void>
  logOut: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<PublicUser | null>(null)
  const [loading, setLoading] = useState(true)

  // The session lives in an HttpOnly cookie, which JavaScript cannot read. Asking the
  // backend who we are is the only way to know, and it survives a page reload.
  useEffect(() => {
    let active = true
    fetchCurrentUser()
      .then((found) => active && setUser(found))
      .catch(() => active && setUser(null))
      .finally(() => active && setLoading(false))
    return () => {
      active = false
    }
  }, [])

  const logIn = useCallback(async (email: string, password: string) => {
    setUser(await postLogin(email, password))
  }, [])

  const signUp = useCallback(async (input: SignupInput) => {
    setUser(await postSignup(input))
  }, [])

  const logOut = useCallback(async () => {
    await postLogout()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, logIn, signUp, logOut }),
    [user, loading, logIn, signUp, logOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return context
}
