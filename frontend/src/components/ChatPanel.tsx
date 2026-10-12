import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { sendChatMessage } from '../api'
import { useAuth } from '../AuthContext'
import { useChat } from '../ChatContext'
import type { ProductSummary } from '../types'

type Message = {
  role: 'user' | 'assistant'
  content: string
  products?: ProductSummary[]
}

const GREETING: Message = {
  role: 'assistant',
  content:
    "Hi — I'm the Campus Customs shop assistant. Ask me about a style, a size, or what we have in stock.",
}

export default function ChatPanel() {
  const { open, prefill, openPanel, closePanel, consumePrefill } = useChat()
  const { user } = useAuth()
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

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
      const reply = await sendChatMessage(message)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply.reply, products: reply.products },
      ])
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
        className="fixed right-5 bottom-5 z-50 cursor-pointer rounded-full bg-accent px-5 py-3 text-sm font-semibold text-white shadow-lg transition-colors hover:bg-ink"
      >
        Ask us anything
      </button>
    )
  }

  return (
    <aside
      aria-label="Shop assistant"
      className="fixed right-5 bottom-5 z-50 flex h-[32rem] w-[22rem] max-w-[calc(100vw-2.5rem)] flex-col overflow-hidden rounded-lg border border-line bg-paper shadow-xl"
    >
      <div className="flex items-center justify-between border-b border-line bg-accent px-4 py-3">
        <h2 className="text-sm font-semibold text-white">Shop assistant</h2>
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
          <div
            key={index}
            className={
              message.role === 'user'
                ? 'ml-auto max-w-[85%] rounded-lg bg-accent px-3 py-2 text-sm text-white'
                : 'mr-auto max-w-[85%] rounded-lg bg-cream px-3 py-2 text-sm text-body'
            }
          >
            {message.content}
          </div>
        ))}
        {sending && (
          <p className="mr-auto rounded-lg bg-cream px-3 py-2 text-sm text-muted italic">
            Thinking…
          </p>
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
          <>Signed in as {user.first_name ?? user.name}.</>
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
          className="flex-1 rounded border border-line bg-cream px-3 py-2 text-sm text-ink placeholder:text-muted"
        />
        <button
          type="submit"
          disabled={sending || !draft.trim()}
          className="cursor-pointer rounded bg-accent px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-ink disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </aside>
  )
}
