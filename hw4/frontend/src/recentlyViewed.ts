/**
 * Recently viewed, for shoppers who are not signed in.
 *
 * Kept in `localStorage`, deliberately. The brief allowed cookies here, but decision D2
 * (output/harness.md) was that signed-out visitors are not tracked by cookie or IP,
 * because it is off-putting. localStorage satisfies both: the list works, and it never
 * leaves the browser — it is not sent with requests, not readable by the server, and not
 * an identifier anyone could track across sites.
 *
 * Signed-in shoppers get the server-side list instead, which follows their account.
 */
const KEY = 'campus_customs_recently_viewed'
const LIMIT = 8

export function readGuestRecentlyViewed(): string[] {
  try {
    const raw = window.localStorage.getItem(KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed.filter((v) => typeof v === 'string') : []
  } catch {
    // Private browsing, a full quota, or corrupted JSON. The feature is a convenience;
    // it must never break the page.
    return []
  }
}

export function recordGuestView(productId: string): void {
  try {
    const next = [productId, ...readGuestRecentlyViewed().filter((id) => id !== productId)]
    window.localStorage.setItem(KEY, JSON.stringify(next.slice(0, LIMIT)))
  } catch {
    /* ignore */
  }
}

export function clearGuestRecentlyViewed(): void {
  try {
    window.localStorage.removeItem(KEY)
  } catch {
    /* ignore */
  }
}
