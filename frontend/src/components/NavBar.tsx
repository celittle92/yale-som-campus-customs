import { NavLink } from 'react-router-dom'

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

        <ul className="ml-auto flex items-center gap-2">
          {accountPages.map((page, index) => (
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
          ))}
        </ul>
      </nav>
    </header>
  )
}
