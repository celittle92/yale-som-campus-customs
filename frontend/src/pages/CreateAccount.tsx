import { Link } from 'react-router-dom'

/**
 * Problem 3 builds the page; signup arrives in a later problem. The form does not
 * submit anywhere and nothing typed into it is stored or sent. When it is wired up,
 * passwords are hashed with Argon2id server-side and never leave the backend.
 */
export default function CreateAccount() {
  return (
    <div className="mx-auto max-w-md px-5 py-12">
      <h1 className="font-display text-3xl font-bold text-ink">Create an account</h1>
      <p className="mt-2 text-body">
        An account keeps your chat with the shop assistant between visits. That is all we
        use it for.
      </p>

      <p className="mt-6 rounded-lg border border-line bg-accent-soft px-4 py-3 text-sm text-body">
        Accounts are not wired up yet — this form is part of the site layout, and it does
        not send anything anywhere.
      </p>

      <form className="mt-6 space-y-4" onSubmit={(event) => event.preventDefault()}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="first-name" className="block text-sm font-medium text-ink">
              First name
            </label>
            <input
              id="first-name"
              type="text"
              autoComplete="given-name"
              disabled
              className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>
          <div>
            <label htmlFor="last-name" className="block text-sm font-medium text-ink">
              Last name
            </label>
            <input
              id="last-name"
              type="text"
              autoComplete="family-name"
              disabled
              className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>
        </div>

        <div>
          <label htmlFor="new-email" className="block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="new-email"
            type="email"
            autoComplete="email"
            disabled
            placeholder="you@yale.edu"
            className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        <div>
          <label htmlFor="new-password" className="block text-sm font-medium text-ink">
            Password
          </label>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            disabled
            className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        <button
          type="submit"
          disabled
          className="w-full rounded bg-accent px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Create account
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
