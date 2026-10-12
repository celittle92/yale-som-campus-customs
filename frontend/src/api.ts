import type { ChatReply, ProductDetail, ProductSummary } from './types'

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
export async function sendChatMessage(message: string): Promise<ChatReply> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!response.ok) {
    throw new Error('The shop assistant is not available right now.')
  }
  return (await response.json()) as ChatReply
}

export function formatPrice(price: number): string {
  // Always two decimals: the catalogue has no cents today, but if it ever gains them
  // the full price must show rather than being silently dropped.
  return price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}
