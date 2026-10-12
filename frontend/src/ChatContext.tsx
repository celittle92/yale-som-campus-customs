import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

type ChatControls = {
  open: boolean
  /** Text to drop into the composer. Cleared once the panel has taken it. */
  prefill: string
  openPanel: () => void
  closePanel: () => void
  /** Open the panel with a question already written, e.g. from a product page. */
  openWith: (text: string) => void
  consumePrefill: () => void
}

const ChatContext = createContext<ChatControls | null>(null)

export function ChatProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [prefill, setPrefill] = useState('')

  const openPanel = useCallback(() => setOpen(true), [])
  const closePanel = useCallback(() => setOpen(false), [])
  const openWith = useCallback((text: string) => {
    setPrefill(text)
    setOpen(true)
  }, [])
  const consumePrefill = useCallback(() => setPrefill(''), [])

  const value = useMemo(
    () => ({ open, prefill, openPanel, closePanel, openWith, consumePrefill }),
    [open, prefill, openPanel, closePanel, openWith, consumePrefill],
  )

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}

export function useChat(): ChatControls {
  const context = useContext(ChatContext)
  if (!context) {
    throw new Error('useChat must be used inside a ChatProvider')
  }
  return context
}
