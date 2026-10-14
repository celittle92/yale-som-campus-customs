import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  deleteChatHistory,
  fetchChatHistory,
  formatPrice,
  sendChatMessage,
} from '../api'
import { useAuth } from '../AuthContext'
import { useChat } from '../ChatContext'
import type { ProductSummary } from '../types'

type Message = {
  role: 'user' | 'assistant'
  content: string
  products?: ProductSummary[]
}

/**
 * Render **bold** spans as bold. Our agent is told not to use markdown, but the seeded
 * conversations in the supplied database contain it, so a returning shopper would
 * otherwise see literal asterisks around a price. Deliberately minimal — it splits on
 * the delimiter and wraps the parts, so no HTML is ever interpreted from message text.
 */
function renderText(text: string) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, index) =>
    index % 2 === 1 ? <strong key={index}>{part}</strong> : part,
  )
}

const GREETING: Message = {
  role: 'assistant',
  content:
    "Hi — I'm the Campus Customs shop assistant. Ask me about a style, a size, or what we have in stock.",
}

export default function ChatPanel() {
  const { open, prefill, openPanel, closePanel, consumePrefill, setResults } = useChat()
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  // Load the saved conversation when a signed-in shopper returns, so they see what they
  // said last time rather than an empty panel that quietly remembers anyway. Guests get
  // an empty list from the API, because nothing was ever stored for them.
  useEffect(() => {
    let active = true
    if (!user) {
      setMessages([GREETING])
      return
    }
    fetchChatHistory()
      .then((stored) => {
        if (!active || stored.length === 0) return
        setMessages([
          GREETING,
          ...stored.map((entry) => ({
            role: entry.role,
            content: entry.content,
            products: entry.products,
          })),
        ])
      })
      .catch(() => {
        /* An empty panel is a fine fallback; never block chatting on this. */
      })
    return () => {
      active = false
    }
  }, [user])

  // A product page can open the panel with the question already written. Take it once,
  // then clear it so reopening the panel later does not resurrect an old question.
  useEffect(() => {
    if (!prefill) return
    setDraft(prefill)
    consumePrefill()
    inputRef.current?.focus()
  }, [prefill, consumePrefill])

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    const message = draft.trim()
    if (!message || sending) return

    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setDraft('')
    setSending(true)
    setError(null)
    try {
      // Tell the backend where the shopper is, so "do you have this in pink?" on a
      // product page resolves to that product.
      const reply = await sendChatMessage(message, location.pathname)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply.reply, products: reply.products },
      ])

      // Publish the matches to the rest of the site, so the Products page can render
      // them as full cards rather than them living only inside this panel.
      if (reply.products.length > 0) {
        setResults({
          label: reply.match_label ?? null,
          products: reply.products,
          question: message,
        })
        // Take the shopper to the page only when they asked to see options. A single
        // product usually means a follow-up about something they are already looking
        // at, and navigating away from that would be rude.
        if (reply.products.length > 1 && !location.pathname.startsWith('/products/')) {
          navigate('/products')
        }
      }
    } catch {
      setError('The shop assistant is not available right now. Please try again.')
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <button
        type="button"
        onClick={openPanel}
        className="group fixed right-5 bottom-5 z-50 flex cursor-pointer items-center gap-2.5 rounded-full bg-accent px-5 py-3.5 text-sm font-semibold text-white shadow-lift transition-all duration-300 ease-[var(--ease-out-soft)] hover:-translate-y-0.5 hover:bg-accent-deep"
      >
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white/70" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-white" />
        </span>
        Ask us anything
      </button>
    )
  }

  return (
    <aside
      aria-label="Shop assistant"
      className="animate-panel-in fixed right-5 bottom-5 z-50 flex h-[34rem] w-[23rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-2xl border border-line bg-paper shadow-panel"
    >
      <div className="flex items-center justify-between bg-accent px-4 py-3.5">
        <div className="flex items-center gap-2.5">
          <span
            aria-hidden="true"
            className="grid h-7 w-7 place-items-center rounded-full bg-white/15 text-[11px] font-semibold text-white"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            CC
          </span>
          <h2 className="text-sm font-semibold text-white">Shop assistant</h2>
        </div>
        <button
          type="button"
          onClick={closePanel}
          aria-label="Close the shop assistant"
          className="cursor-pointer rounded px-2 text-xl leading-none text-white/80 hover:text-white"
        >
          &times;
        </button>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-3">
        {messages.map((message, index) => (
          <div key={index}>
            <div
              // whitespace-pre-line keeps the assistant's line breaks, so a short list
              // of products reads as a list rather than one run-on sentence.
              className={
                message.role === 'user'
                  ? 'animate-bubble-in ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-accent px-3.5 py-2.5 text-sm whitespace-pre-line text-white shadow-sm'
                  : 'animate-bubble-in mr-auto w-fit max-w-[85%] rounded-2xl rounded-bl-md bg-sand px-3.5 py-2.5 text-sm whitespace-pre-line text-body'
              }
            >
              {renderText(message.content)}
            </div>

            {/* Cards the assistant chose to show. Every one is a real catalogue row
                resolved by the backend from a product id, so the price and image here
                came out of the database, not out of the model. */}
            {message.products && message.products.length > 0 && (
              <ul className="mt-2 space-y-2">
                {message.products.map((product) => (
                  <li key={product.product_id}>
                    <Link
                      to={`/products/${product.product_id}`}
                      onClick={closePanel}
                      className="flex items-center gap-3 rounded-xl border border-line bg-paper p-2 transition-all duration-300 hover:-translate-y-px hover:border-accent/40 hover:shadow-card"
                    >
                      <img
                        src={product.image_url}
                        alt={product.name}
                        loading="lazy"
                        className="h-14 w-14 flex-none rounded object-cover"
                      />
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-medium text-ink">
                          {product.name}
                        </span>
                        <span className="block text-sm text-accent">
                          {formatPrice(product.price)}
                        </span>
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {sending && (
          <div
            role="status"
            aria-label="The shop assistant is replying"
            className="animate-bubble-in mr-auto flex w-fit items-center gap-1.5 rounded-2xl rounded-bl-md bg-sand px-4 py-3"
          >
            <span className="dot h-1.5 w-1.5 rounded-full bg-muted" />
            <span className="dot h-1.5 w-1.5 rounded-full bg-muted" />
            <span className="dot h-1.5 w-1.5 rounded-full bg-muted" />
          </div>
        )}
        {error && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">
            {error}
          </p>
        )}
        <div ref={endRef} />
      </div>

      {/* Decision D2: nothing a signed-out visitor types is stored, so say so rather
          than letting someone lose a conversation they assumed was saved. */}
      <p className="border-t border-line px-4 py-2 text-xs text-muted">
        {user ? (
          <>
            Signed in as {user.first_name ?? user.name}. This chat is saved.{' '}
            <button
              type="button"
              onClick={async () => {
                await deleteChatHistory()
                setMessages([GREETING])
              }}
              className="cursor-pointer underline hover:text-accent"
            >
              Clear it
            </button>
          </>
        ) : (
          <>
            Not signed in, so this chat is not saved.{' '}
            <Link to="/login" className="underline hover:text-accent">
              Log in
            </Link>{' '}
            to keep it.
          </>
        )}
      </p>

      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-line p-3">
        <label htmlFor="chat-input" className="sr-only">
          Message the shop assistant
        </label>
        <input
          id="chat-input"
          ref={inputRef}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Do you have hoodies in XL?"
          maxLength={2000}
          className="flex-1 rounded-full border border-line bg-cream px-4 py-2.5 text-sm text-ink transition-colors placeholder:text-muted focus:border-accent"
        />
        <button
          type="submit"
          disabled={sending || !draft.trim()}
          className="cursor-pointer rounded-full bg-accent px-4 py-2.5 text-sm font-semibold text-white transition-all duration-300 hover:bg-accent-deep disabled:cursor-not-allowed disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </aside>
  )
}
