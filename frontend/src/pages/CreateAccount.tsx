import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const MIN_PASSWORD = 8

export default function CreateAccount() {
  const { user, signUp } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirm_password: '',
  })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  function update(field: keyof typeof form) {
    return (event: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const mismatch =
    form.confirm_password.length > 0 && form.password !== form.confirm_password
  const tooShort = form.password.length > 0 && form.password.length < MIN_PASSWORD
  const complete =
    form.first_name && form.last_name && form.email && form.password && form.confirm_password

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    // Checked here for a fast, clear message; the backend checks again, because
    // client-side validation is a courtesy and not a control.
    if (form.password !== form.confirm_password) {
      setError('The two passwords do not match.')
      return
    }
    setBusy(true)
    try {
      await signUp(form)
      setForm((prev) => ({ ...prev, password: '', confirm_password: '' }))
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
        <h1 className="font-display text-3xl font-bold text-ink">
          Your account is ready
        </h1>
        <p className="mt-3 text-body">
          Signed in as <span className="font-semibold">{user.name}</span> ({user.email}).
        </p>
        <Link
          to="/products"
          className="mt-6 inline-block rounded bg-accent px-5 py-3 text-sm font-semibold text-white hover:bg-ink"
        >
          Start shopping
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md px-5 py-12">
      <h1 className="font-display text-3xl font-bold text-ink">Create an account</h1>
      <p className="mt-2 text-body">
        An account keeps your chat with the shop assistant between visits. That is all we
        use it for.
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

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="first-name" className="block text-sm font-medium text-ink">
              First name
            </label>
            <input
              id="first-name"
              name="first_name"
              type="text"
              required
              autoComplete="given-name"
              value={form.first_name}
              onChange={update('first_name')}
              className="mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink"
            />
          </div>
          <div>
            <label htmlFor="last-name" className="block text-sm font-medium text-ink">
              Last name
            </label>
            <input
              id="last-name"
              name="last_name"
              type="text"
              required
              autoComplete="family-name"
              value={form.last_name}
              onChange={update('last_name')}
              className="mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink"
            />
          </div>
        </div>

        <div>
          <label htmlFor="new-email" className="block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="new-email"
            name="email"
            type="email"
            required
            autoComplete="email"
            value={form.email}
            onChange={update('email')}
            placeholder="you@yale.edu"
            className="mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink"
          />
        </div>

        <div>
          <label htmlFor="new-password" className="block text-sm font-medium text-ink">
            Password
          </label>
          <input
            id="new-password"
            name="password"
            type="password"
            required
            minLength={MIN_PASSWORD}
            autoComplete="new-password"
            value={form.password}
            onChange={update('password')}
            aria-describedby="password-hint"
            className="mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink"
          />
          <p
            id="password-hint"
            className={tooShort ? 'mt-1 text-xs text-red-700' : 'mt-1 text-xs text-muted'}
          >
            At least {MIN_PASSWORD} characters.
          </p>
        </div>

        <div>
          <label htmlFor="confirm-password" className="block text-sm font-medium text-ink">
            Confirm password
          </label>
          <input
            id="confirm-password"
            name="confirm_password"
            type="password"
            required
            autoComplete="new-password"
            value={form.confirm_password}
            onChange={update('confirm_password')}
            aria-invalid={mismatch}
            aria-describedby={mismatch ? 'confirm-error' : undefined}
            className={
              mismatch
                ? 'mt-1 w-full rounded border border-red-400 bg-paper px-3 py-2 text-ink'
                : 'mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink'
            }
          />
          {mismatch && (
            <p id="confirm-error" className="mt-1 text-xs text-red-700">
              The two passwords do not match.
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={busy || !complete || mismatch || tooShort}
          className="w-full cursor-pointer rounded bg-accent px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ink disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? 'Creating your account…' : 'Create account'}
        </button>
      </form>

      <p className="mt-6 text-sm text-body">
        Already have one?{' '}
        <Link to="/login" className="text-accent underline">
          Log in
        </Link>
        .
      </p>
    </div>
  )
}
