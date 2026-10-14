import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { ProductSummary } from '../types'

type Props = {
  title: string
  products: ProductSummary[]
  subtitle?: string
  action?: { label: string; onClick: () => void }
}

/**
 * A horizontally scrollable row of products, used for "You might also like" and
 * "Recently viewed".
 *
 * Each item is the same kind of link as a product card, so it opens the single-item
 * page exactly like everything else on the site.
 */
export default function ProductRow({ title, products, subtitle, action }: Props) {
  if (products.length === 0) return null
  const headingId = `row-${title.replace(/\s+/g, '-').toLowerCase()}`

  return (
    <section aria-labelledby={headingId} className="mt-12">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <div>
          <h2 id={headingId} className="font-display text-2xl font-bold text-ink">
            {title}
          </h2>
          {subtitle && <p className="mt-1 text-sm text-body">{subtitle}</p>}
        </div>
        {action && (
          <button
            type="button"
            onClick={action.onClick}
            className="cursor-pointer text-sm text-accent underline"
          >
            {action.label}
          </button>
        )}
      </div>

      {/* Scroll-snap keeps cards aligned as you swipe; the row scrolls with a trackpad,
          a touch swipe, or the keyboard once focused. */}
      <ul className="mt-5 flex snap-x snap-mandatory gap-5 overflow-x-auto pb-4">
        {products.map((product) => (
          <li key={product.product_id} className="w-56 flex-none snap-start">
            <Link
              to={`/products/${product.product_id}`}
              className="group flex h-full flex-col overflow-hidden rounded-lg border border-line bg-paper transition-shadow hover:shadow-md"
            >
              <div className="aspect-square overflow-hidden bg-cream">
                <img
                  src={product.image_url}
                  alt={product.name}
                  loading="lazy"
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </div>
              <div className="flex flex-1 flex-col gap-1 p-3">
                <h3 className="text-sm leading-snug font-semibold text-ink">
                  {product.name}
                </h3>
                <span className="mt-auto text-sm font-semibold text-accent">
                  {formatPrice(product.price)}
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
