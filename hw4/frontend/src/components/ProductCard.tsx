import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { ProductSummary } from '../types'

type Props = {
  product: ProductSummary
  /** Stock for this product, when the page has it, so the card can be honest. */
  stock?: Record<string, number>
  /** Staggers the entrance so a grid resolves in sequence rather than all at once. */
  index?: number
}

export default function ProductCard({ product, stock, index = 0 }: Props) {
  const quantities = stock ? Object.values(stock) : []
  const total = quantities.reduce((a, b) => a + b, 0)
  const sizesLeft = quantities.filter((q) => q > 0).length
  const soldOut = quantities.length > 0 && total === 0
  // Scarcity, but only when it is true: two or fewer sizes still available.
  const scarce = !soldOut && sizesLeft > 0 && sizesLeft <= 2

  return (
    <li
      className="animate-rise"
      style={{ animationDelay: `${Math.min(index, 11) * 45}ms` }}
    >
      <Link
        to={`/products/${product.product_id}`}
        className="group flex h-full flex-col overflow-hidden rounded-xl border border-line bg-paper shadow-card transition-all duration-500 ease-[var(--ease-out-soft)] hover:-translate-y-1 hover:border-accent/30 hover:shadow-lift focus-visible:-translate-y-1"
      >
        <div className="relative aspect-square overflow-hidden bg-sand">
          <img
            src={product.image_url}
            alt={product.name}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-700 ease-[var(--ease-out-soft)] group-hover:scale-[1.07]"
          />

          {soldOut && (
            <span className="absolute top-3 left-3 rounded-full bg-ink/85 px-3 py-1 text-[11px] font-semibold tracking-wide text-white backdrop-blur-sm">
              Sold out
            </span>
          )}
          {scarce && (
            <span className="absolute top-3 left-3 rounded-full bg-low-soft px-3 py-1 text-[11px] font-semibold tracking-wide text-low">
              Only {sizesLeft} {sizesLeft === 1 ? 'size' : 'sizes'} left
            </span>
          )}

          {/* A quiet cue that the whole card is a target, revealed on hover. */}
          <span
            aria-hidden="true"
            className="pointer-events-none absolute right-3 bottom-3 translate-y-2 rounded-full bg-paper/95 px-3 py-1.5 text-xs font-semibold text-accent opacity-0 shadow-sm transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100"
          >
            View details →
          </span>
        </div>

        <div className="flex flex-1 flex-col gap-2 p-5">
          <h3 className="font-display text-lg leading-snug font-semibold text-ink">
            {product.name}
          </h3>
          <p className="line-clamp-2 flex-1 text-sm leading-relaxed text-body">
            {product.description}
          </p>
          <div className="mt-2 flex items-baseline justify-between gap-3 border-t border-line/70 pt-3">
            <span className="flex-none font-display text-lg font-semibold text-accent">
              {formatPrice(product.price)}
            </span>
            {/* Long cuts like "quarter-zip pullover sweatshirt" must not crowd the
                price, which is the number a shopper is actually scanning for. */}
            <span className="truncate text-right text-[11px] tracking-wide text-muted uppercase">
              {product.garment_type}
            </span>
          </div>
        </div>
      </Link>
    </li>
  )
}
