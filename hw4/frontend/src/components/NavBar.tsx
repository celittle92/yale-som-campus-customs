import { NavLink } from 'react-router-dom'
import { useAuth } from '../AuthContext'

const pages = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products', end: false },
  { to: '/about', label: 'About Us', end: false },
]

function linkClass({ isActive }: { isActive: boolean }): string {
  const base =
    'relative rounded px-1 py-2 text-sm transition-colors after:absolute after:inset-x-1 after:-bottom-0.5 after:h-px after:origin-left after:scale-x-0 after:bg-accent after:transition-transform after:duration-300 hover:after:scale-x-100'
  return isActive
    ? `${base} font-semibold text-accent after:scale-x-100`
    : `${base} text-body hover:text-ink`
}

/** A quiet monogram, so the wordmark has something to sit against. */
function Monogram() {
  return (
    <span
      aria-hidden="true"
      className="grid h-9 w-9 flex-none place-items-center rounded-full bg-accent text-[13px] font-semibold tracking-tight text-white transition-transform duration-300 group-hover:scale-105"
      style={{ fontFamily: 'var(--font-display)' }}
    >
      CC
    </span>
  )
}

export default function NavBar() {
  const { user, loading, logOut } = useAuth()

  return (
    <header className="sticky top-0 z-40 border-b border-line/70 bg-cream/85 backdrop-blur-md">
      <nav
        aria-label="Main"
        className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-8 gap-y-3 px-5 py-3.5"
      >
        <NavLink to="/" className="group flex items-center gap-3">
          <Monogram />
          <span className="leading-none">
            <span className="block font-display text-xl font-semibold tracking-tight text-ink">
              Campus Customs
            </span>
            <span className="mt-0.5 block text-[10px] font-medium tracking-[0.18em] text-muted uppercase">
              New Haven
            </span>
          </span>
        </NavLink>

        <ul className="flex items-center gap-6">
          {pages.map((page) => (
            <li key={page.to}>
              <NavLink to={page.to} end={page.end} className={linkClass}>
                {page.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <ul className="ml-auto flex items-center gap-3">
          {loading ? null : user ? (
            <>
              <li className="hidden text-sm text-body sm:block">
                Hi,{' '}
                <span className="font-semibold text-ink">
                  {user.first_name ?? user.name}
                </span>
              </li>
              <li>
                <button
                  type="button"
                  onClick={() => void logOut()}
                  className="cursor-pointer rounded-full border border-line px-4 py-2 text-sm font-medium text-ink transition-colors hover:border-accent hover:bg-accent-soft"
                >
                  Log out
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink
                  to="/login"
                  className="rounded-full px-3 py-2 text-sm text-body transition-colors hover:text-ink"
                >
                  Log In
                </NavLink>
              </li>
              <li>
                <NavLink
                  to="/create-account"
                  className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-px hover:bg-accent-deep hover:shadow-card"
                >
                  Create Account
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  )
}
