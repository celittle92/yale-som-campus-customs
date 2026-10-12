import { Link } from 'react-router-dom'

/**
 * Problem 3 builds the page; authentication arrives in a later problem. The form does
 * not submit anywhere and nothing typed into it is stored or sent.
 */
export default function LogIn() {
  return (
    <div className="mx-auto max-w-md px-5 py-12">
      <h1 className="font-display text-3xl font-bold text-ink">Log in</h1>
      <p className="mt-2 text-body">
        Logging in keeps your chat with the shop assistant, so you do not have to explain
        yourself twice.
      </p>

      <p className="mt-6 rounded-lg border border-line bg-accent-soft px-4 py-3 text-sm text-body">
        Accounts are not wired up yet — this form is part of the site layout, and it does
        not send anything anywhere.
      </p>

      <form
        className="mt-6 space-y-4"
        onSubmit={(event) => event.preventDefault()}
        aria-describedby="login-status"
      >
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-ink">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            disabled
            placeholder="you@yale.edu"
            className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-ink">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            disabled
            className="mt-1 w-full rounded border border-line bg-cream px-3 py-2 text-ink disabled:cursor-not-allowed disabled:opacity-60"
          />
        </div>

        <button
          type="submit"
          disabled
          className="w-full rounded bg-accent px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          Log in
        </button>
      </form>

      <p id="login-status" className="mt-6 text-sm text-body">
        No account yet?{' '}
        <Link to="/create-account" className="text-accent underline">
          Create one
        </Link>
        .
      </p>
    </div>
  )
}
