import { useEffect, useMemo, useState } from 'react'
import ProductCard from '../components/ProductCard'
import ProductFilter, {
  applyFilters,
  EMPTY_FILTERS,
  type Filters,
} from '../components/ProductFilter'
import ProductRow from '../components/ProductRow'
import {
  clearRecentlyViewed,
  fetchProducts,
  fetchProductsByIds,
  fetchRecentlyViewed,
  fetchStock,
} from '../api'
import { useAuth } from '../AuthContext'
import { useChat } from '../ChatContext'
import {
  clearGuestRecentlyViewed,
  readGuestRecentlyViewed,
} from '../recentlyViewed'
import type { ProductSummary } from '../types'

export default function Products() {
  const [products, setProducts] = useState<ProductSummary[] | null>(null)
  const [stock, setStock] = useState<Record<string, Record<string, number>>>({})
  const [filters, setFilters] = useState<Filters>(EMPTY_FILTERS)
  const [recent, setRecent] = useState<ProductSummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const { results, setResults, openPanel } = useChat()
  const { user } = useAuth()

  useEffect(() => {
    let active = true
    fetchProducts()
      .then((data) => active && setProducts(data))
      .catch((caught: Error) => active && setError(caught.message))
    // The filter needs stock, but the grid should not wait for it.
    fetchStock()
      .then((data) => active && setStock(data))
      .catch(() => {
        /* filtering by size degrades gracefully; the grid still works */
      })
    return () => {
      active = false
    }
  }, [])

  // Signed in: the server-side list, which follows the account. Signed out: whatever
  // their own browser remembers, which never left it.
  useEffect(() => {
    let active = true
    const load = user
      ? fetchRecentlyViewed()
      : fetchProductsByIds(readGuestRecentlyViewed())
    load.then((data) => active && setRecent(data)).catch(() => undefined)
    return () => {
      active = false
    }
  }, [user])

  const visible = useMemo(
    () => (products ? applyFilters(products, filters, stock) : []),
    [products, filters, stock],
  )

  const filtering =
    !!filters.type || !!filters.color || !!filters.size || filters.inStockOnly

  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <h1 className="font-display text-4xl font-bold text-ink">Products</h1>
      <p className="mt-3 max-w-2xl text-body">
        Everything we stock, in sizes XS through XXL. Open any item to see the full
        description and which sizes are left.
      </p>

      {/* Matches the shop assistant put here. Same ProductCard as the grid below, so a
          card from chat opens the single-item page exactly like any other. */}
      {results && results.products.length > 0 && (
        <section
          aria-labelledby="chat-results-heading"
          className="mt-10 rounded-lg border border-accent/30 bg-accent-soft p-6"
        >
          <div className="flex flex-wrap items-baseline justify-between gap-3">
            <div>
              <h2
                id="chat-results-heading"
                className="font-display text-2xl font-bold text-ink"
              >
                {results.label ?? 'From your chat'}
              </h2>
              <p className="mt-1 text-sm text-body">
                {results.products.length}{' '}
                {results.products.length === 1 ? 'match' : 'matches'} for “
                {results.question}”
              </p>
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={openPanel}
                className="cursor-pointer rounded border border-line bg-paper px-4 py-2 text-sm font-semibold text-ink transition-colors hover:border-accent"
              >
                Back to chat
              </button>
              <button
                type="button"
                onClick={() => setResults(null)}
                className="cursor-pointer rounded px-4 py-2 text-sm text-body underline transition-colors hover:text-accent"
              >
                Clear
              </button>
            </div>
          </div>
          <ul className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {results.products.map((product, i) => (
              <ProductCard
                key={product.product_id}
                product={product}
                stock={stock[product.product_id]}
                index={i}
              />
            ))}
          </ul>
        </section>
      )}

      <ProductRow
        title="Recently viewed"
        subtitle={
          user
            ? 'Saved to your account, so it follows you between visits.'
            : 'Kept in this browser only. Log in to keep it between visits.'
        }
        products={recent}
        action={{
          label: 'Clear',
          onClick: () => {
            if (user) void clearRecentlyViewed()
            else clearGuestRecentlyViewed()
            setRecent([])
          },
        }}
      />

      {error && (
        <p
          role="alert"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-red-800"
        >
          {error} Check that the backend is running on port 8000.
        </p>
      )}

      {/* Skeletons rather than a line of text: loading reads as "coming", and the
          page does not jump when the real cards arrive. */}
      {!products && !error && (
        <>
          <div className="skeleton mt-8 h-32 rounded-lg" />
          <ul className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <li key={i} className="overflow-hidden rounded-xl border border-line bg-paper">
                <div className="skeleton aspect-square" />
                <div className="space-y-3 p-5">
                  <div className="skeleton h-4 w-3/4 rounded" />
                  <div className="skeleton h-3 w-full rounded" />
                  <div className="skeleton h-3 w-2/3 rounded" />
                  <div className="skeleton h-4 w-20 rounded" />
                </div>
              </li>
            ))}
          </ul>
        </>
      )}

      {products && (
        <>
          <ProductFilter
            products={products}
            filters={filters}
            onChange={setFilters}
            matchCount={visible.length}
          />

          {visible.length === 0 ? (
            <div className="mt-10 rounded-lg border border-line bg-paper p-8 text-center">
              <p className="text-ink">Nothing matches those filters.</p>
              <p className="mt-1 text-sm text-body">
                {filters.size
                  ? `We may carry it in another size — try clearing the size filter.`
                  : 'Try widening one of them.'}
              </p>
              <button
                type="button"
                onClick={() => setFilters(EMPTY_FILTERS)}
                className="mt-4 cursor-pointer rounded bg-accent px-5 py-2 text-sm font-semibold text-white hover:bg-ink"
              >
                Clear filters
              </button>
            </div>
          ) : (
            <>
              <h2 className="mt-10 font-display text-2xl font-bold text-ink">
                {filtering ? 'Matching products' : 'All products'}
              </h2>
              <p className="mt-1 text-sm text-muted">
                {visible.length} {visible.length === 1 ? 'style' : 'styles'}
              </p>
              <ul className="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {visible.map((product, i) => (
                  <ProductCard
                    key={product.product_id}
                    product={product}
                    stock={stock[product.product_id]}
                    index={i}
                  />
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </div>
  )
}
