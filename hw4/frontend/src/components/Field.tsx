import type { InputHTMLAttributes } from 'react'

type Props = {
  id: string
  label: string
  error: string | null
  hint?: string
} & InputHTMLAttributes<HTMLInputElement>

/**
 * A labelled input that shows its own validation message.
 *
 * The error is wired to the input with `aria-describedby` and `aria-invalid`, and the
 * message carries `role="alert"`, so a screen reader announces the problem rather than
 * leaving it as a red colour a sighted user alone can see.
 */
export default function Field({ id, label, error, hint, ...input }: Props) {
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined

  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-ink">
        {label}
      </label>
      <input
        id={id}
        aria-invalid={!!error}
        aria-describedby={describedBy}
        className={
          error
            ? 'mt-1 w-full rounded border-2 border-red-400 bg-paper px-3 py-2 text-ink'
            : 'mt-1 w-full rounded border border-line bg-paper px-3 py-2 text-ink'
        }
        {...input}
      />
      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-1 text-xs font-medium text-red-700">
          {error}
        </p>
      ) : hint ? (
        <p id={`${id}-hint`} className="mt-1 text-xs text-muted">
          {hint}
        </p>
      ) : null}
    </div>
  )
}
