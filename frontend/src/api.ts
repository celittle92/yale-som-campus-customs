import type {
  ChatHistoryMessage,
  ChatReply,
  ProductDetail,
  ProductSummary,
  PublicUser,
  SignupInput,
} from './types'

// Everything goes through the FastAPI backend on the same origin (Vite proxies /api in
// development). No API key ever reaches the browser.
async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(
      response.status === 404
        ? 'We could not find that.'
        : `The shop is not responding right now (${response.status}).`,
    )
  }
  return (await response.json()) as T
}

export function fetchProducts(): Promise<ProductSummary[]> {
  return getJSON<ProductSummary[]>('/api/products')
}

export function fetchProduct(productId: string): Promise<ProductDetail> {
  return getJSON<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`)
}

/**
 * Problem 3 ships the stub backend route, which answers in the shape the real agent
 * will use. Problem 5 swaps the implementation behind this call; nothing here changes.
 */
export async function sendChatMessage(
  message: string,
  pagePath?: string,
): Promise<ChatReply> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    // Only the path is sent. The backend decides what it means and looks the product
    // up itself, so the browser cannot assert which product is being discussed.
    body: JSON.stringify({ message, page_path: pagePath ?? null }),
  })
  if (!response.ok) {
    throw new Error('The shop assistant is not available right now.')
  }
  return (await response.json()) as ChatReply
}

/** A signed-in shopper's saved conversation. Empty for guests. */
export async function fetchChatHistory(): Promise<ChatHistoryMessage[]> {
  const response = await fetch('/api/chat/history')
  if (!response.ok) return []
  return (await response.json()) as ChatHistoryMessage[]
}

export async function deleteChatHistory(): Promise<void> {
  await fetch('/api/chat/history', { method: 'DELETE' })
}

/**
 * Auth. The password is sent once over the request body and is never stored in the
 * browser — not in state after submit, not in localStorage, not in a cookie we set.
 * The session is an HttpOnly cookie the backend sets, which JavaScript cannot read.
 */
async function postAuth<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    let detail = 'Something went wrong. Please try again.'
    try {
      const problem = await response.json()
      if (typeof problem.detail === 'string') {
        detail = problem.detail
      } else if (Array.isArray(problem.detail) && problem.detail[0]?.msg) {
        // FastAPI validation errors arrive as a list; show the first plainly.
        detail = String(problem.detail[0].msg).replace(/^Value error,\s*/, '')
      }
    } catch {
      // Keep the generic message.
    }
    throw new Error(detail)
  }
  return (await response.json()) as T
}

export function postLogin(email: string, password: string): Promise<PublicUser> {
  return postAuth<PublicUser>('/api/auth/login', { email, password })
}

export function postSignup(input: SignupInput): Promise<PublicUser> {
  return postAuth<PublicUser>('/api/auth/signup', input)
}

export async function postLogout(): Promise<void> {
  await fetch('/api/auth/logout', { method: 'POST' })
}

export async function fetchCurrentUser(): Promise<PublicUser | null> {
  const response = await fetch('/api/auth/me')
  if (!response.ok) return null
  return (await response.json()) as PublicUser | null
}

export function formatPrice(price: number): string {
  // Always two decimals: the catalogue has no cents today, but if it ever gains them
  // the full price must show rather than being silently dropped.
  return price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
