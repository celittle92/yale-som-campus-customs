import { NavLink } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const pages = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products', end: false },
  { to: '/about', label: 'About Us', end: false },
]

const accountPages = [
  { to: '/login', label: 'Log In' },
  { to: '/create-account', label: 'Create Account' },
]

function linkClass({ isActive }: { isActive: boolean }): string {
  const base = 'rounded px-3 py-2 text-sm transition-colors'
  return isActive
    ? `${base} bg-accent-soft font-semibold text-accent`
    : `${base} text-body hover:bg-accent-soft hover:text-accent`
}

export default function NavBar() {
  const { user, loading, logOut } = useAuth()
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/95 backdrop-blur">
      <nav
        aria-label="Main"
        className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-3 px-5 py-4"
      >
        <NavLink
          to="/"
          className="font-display text-xl font-bold tracking-tight text-ink"
        >
          Campus Customs
          <span className="ml-2 align-middle text-xs font-normal tracking-widest text-muted uppercase">
            New Haven
          </span>
        </NavLink>

        <ul className="flex items-center gap-1">
          {pages.map((page) => (
            <li key={page.to}>
              <NavLink to={page.to} end={page.end} className={linkClass}>
                {page.label}
              </NavLink>
            </li>
          ))}
        </ul>

        {/* Signed in: greet by first name and offer a way out. Signed out: the two
            account links. Nothing renders until /api/auth/me settles, so the nav does
            not flash "Log In" at someone who already is. */}
        <ul className="ml-auto flex items-center gap-2">
          {loading ? null : user ? (
            <>
              <li className="text-sm text-body">
                Hi,{' '}
                <span className="font-semibold text-ink">
                  {user.first_name ?? user.name}
                </span>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => void logOut()}
                  className="cursor-pointer rounded border border-line px-4 py-2 text-sm font-semibold text-ink transition-colors hover:bg-accent-soft"
                >
                  Log out
                </button>
              </li>
            </>
          ) : (
            accountPages.map((page, index) => (
              <li key={page.to}>
                <NavLink
                  to={page.to}
                  className={
                    index === accountPages.length - 1
                      ? 'rounded bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-ink'
                      : linkClass
                  }
                >
                  {page.label}
                </NavLink>
              </li>
            ))
          )}
        </ul>
      </nav>
    </header>
  )
}
