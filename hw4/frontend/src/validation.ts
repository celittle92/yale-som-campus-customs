/**
 * Inline form validation.
 *
 * Pure functions, so the same rules can be read, tested and reused by both forms, and
 * so the message a shopper sees is defined in one place.
 *
 * The timing rule matters as much as the rule itself. Complaining on the first keystroke
 * is obnoxious — nobody has typed a valid email after one character. These return an
 * error as soon as the input is *recognisably* wrong, and the forms also show errors
 * once a field has been left, so you learn early without being nagged.
 */

export const MIN_PASSWORD = 8

/** Long enough to be a real attempt, so "c" is not called an invalid email. */
const ENOUGH_TO_JUDGE = 4

export function emailError(value: string, touched: boolean): string | null {
  const trimmed = value.trim()
  if (!trimmed) return touched ? 'Enter your email address.' : null
  if (!touched && trimmed.length < ENOUGH_TO_JUDGE) return null

  if (!trimmed.includes('@')) return 'An email address needs an @ symbol.'
  const [local, ...rest] = trimmed.split('@')
  if (rest.length > 1) return 'An email address can only have one @ symbol.'
  const domain = rest[0] ?? ''
  if (!local) return 'Add the part before the @.'
  if (!domain) return 'Add the part after the @, such as yale.edu.'
  // Only insist on a dot once they have started the domain, so "you@y" is not yelled at.
  if (touched && !domain.includes('.')) return 'The domain needs a dot, such as yale.edu.'
  if (/\s/.test(trimmed)) return 'An email address cannot contain spaces.'
  return null
}

export function passwordError(value: string, touched: boolean): string | null {
  if (!value) return touched ? 'Enter a password.' : null
  if (value.length < MIN_PASSWORD) {
    const missing = MIN_PASSWORD - value.length
    return `${missing} more character${missing === 1 ? '' : 's'} needed.`
  }
  return null
}

export function confirmError(password: string, confirm: string): string | null {
  if (!confirm) return null
  return password === confirm ? null : 'The two passwords do not match.'
}

export function requiredError(value: string, label: string, touched: boolean): string | null {
  if (value.trim()) return null
  return touched ? `Enter your ${label}.` : null
}
