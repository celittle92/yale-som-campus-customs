import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Field from '../components/Field'
import { useAuth } from '../AuthContext'
import { emailError } from '../validation'

export default function LogIn() {
  const { user, logIn, logOut } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [touched, setTouched] = useState({ email: false, password: false })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  // Checked as they type, so a missing @ is caught before they ever press the button.
  const emailProblem = emailError(email, touched.email)
  const passwordProblem = !password && touched.password ? 'Enter your password.' : null
  const canSubmit = !!email && !!password && !emailProblem && !busy

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setTouched({ email: true, password: true })
    if (!email || !password || emailError(email, true)) return
    setError(null)
    setBusy(true)
    try {
      await logIn(email, password)
      setPassword('')
      navigate('/products')
    } catch (caught) {
      setError((caught as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (user) {
    return (
      <div className="mx-auto max-w-md px-5 py-12">
        <h1 className="font-display text-3xl font-bold text-ink">You are logged in</h1>
        <p className="mt-3 text-body">
          Signed in as <span className="font-semibold">{user.name}</span> ({user.email}).
          Your chat with the shop assistant is saved to this account.
        </p>
        <button
          type="button"
          onClick={() => void logOut()}
          className="mt-6 cursor-pointer rounded border border-line px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-accent-soft"
        >
          Log out
        </button>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md px-5 py-12">
      <h1 className="font-display text-3xl font-bold text-ink">Log in</h1>
      <p className="mt-2 text-body">
        Logging in keeps your chat with the shop assistant, so you do not have to explain
        yourself twice.
      </p>

      <form className="mt-8 space-y-4" onSubmit={handleSubmit} noValidate>
        {error && (
          <p
            role="alert"
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
          >
            {error}
          </p>
        )}

        <Field
          id="email"
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@yale.edu"
          value={email}
          error={emailProblem}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, email: true }))}
        />

        <Field
          id="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          value={password}
          error={passwordProblem}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, password: true }))}
        />

        <button
          type="submit"
          disabled={!canSubmit}
          className="w-full cursor-pointer rounded bg-accent px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ink disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? 'Checking…' : 'Log in'}
        </button>
      </form>

      <p className="mt-6 text-sm text-body">
        No account yet?{' '}
        <Link to="/create-account" className="text-accent underline">
          Create one
        </Link>
        .
      </p>
    </div>
  )
}
