import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Field from '../components/Field'
import { useAuth } from '../AuthContext'
import {
  confirmError,
  emailError,
  MIN_PASSWORD,
  passwordError,
  requiredError,
} from '../validation'

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
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const update = (field: keyof typeof form) => (event: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }))
  const blur = (field: string) => () => setTouched((t) => ({ ...t, [field]: true }))

  // Every rule runs on every keystroke, so problems surface while the shopper is still
  // looking at the field rather than after a round trip to the server.
  const problems = {
    first_name: requiredError(form.first_name, 'first name', !!touched.first_name),
    last_name: requiredError(form.last_name, 'last name', !!touched.last_name),
    email: emailError(form.email, !!touched.email),
    password: passwordError(form.password, !!touched.password),
    confirm_password: confirmError(form.password, form.confirm_password),
  }
  const complete = Object.values(form).every((v) => v.trim())
  const clean = Object.values(problems).every((p) => p === null)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    setTouched({
      first_name: true,
      last_name: true,
      email: true,
      password: true,
      confirm_password: true,
    })
    if (!complete || !clean) return
    setError(null)
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
        <h1 className="font-display text-3xl font-bold text-ink">Your account is ready</h1>
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
          <Field
            id="first-name"
            label="First name"
            type="text"
            autoComplete="given-name"
            value={form.first_name}
            error={problems.first_name}
            onChange={update('first_name')}
            onBlur={blur('first_name')}
          />
          <Field
            id="last-name"
            label="Last name"
            type="text"
            autoComplete="family-name"
            value={form.last_name}
            error={problems.last_name}
            onChange={update('last_name')}
            onBlur={blur('last_name')}
          />
        </div>

        <Field
          id="new-email"
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@yale.edu"
          value={form.email}
          error={problems.email}
          onChange={update('email')}
          onBlur={blur('email')}
        />

        <Field
          id="new-password"
          label="Password"
          type="password"
          autoComplete="new-password"
          value={form.password}
          error={problems.password}
          hint={`At least ${MIN_PASSWORD} characters.`}
          onChange={update('password')}
          onBlur={blur('password')}
        />

        <Field
          id="confirm-password"
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          value={form.confirm_password}
          error={problems.confirm_password}
          onChange={update('confirm_password')}
          onBlur={blur('confirm_password')}
        />

        <button
          type="submit"
          disabled={busy || !complete || !clean}
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
