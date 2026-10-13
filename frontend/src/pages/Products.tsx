import { useEffect, useState } from 'react'
import ProductCard from '../components/ProductCard'
import { fetchProducts } from '../api'
import { useChat } from '../ChatContext'
import type { ProductSummary } from '../types'

export default function Products() {
  const [products, setProducts] = useState<ProductSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { results, setResults, openPanel } = useChat()

  useEffect(() => {
    let active = true
    fetchProducts()
      .then((data) => active && setProducts(data))
      .catch((caught: Error) => active && setError(caught.message))
    return () => {
      active = false
    }
  }, [])

  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <h1 className="font-display text-4xl font-bold text-ink">Products</h1>
      <p className="mt-3 max-w-2xl text-body">
        Everything we stock, in sizes XS through XXL. Open any item to see the full
        description and which sizes are left.
      </p>

      {/* Matches the shop assistant put here. These are the same ProductCard used by the
          full grid below, so a card from chat behaves exactly like any other: clicking
          it opens the single-item page from Problem 3. */}
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
            {results.products.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </ul>
        </section>
      )}

      {error && (
        <p
          role="alert"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-red-800"
        >
          {error} Check that the backend is running on port 8000.
        </p>
      )}

      {!products && !error && <p className="mt-8 text-muted">Loading the catalogue…</p>}

      {products && (
        <>
          <h2 className="mt-12 font-display text-2xl font-bold text-ink">
            {results && results.products.length > 0 ? 'Everything else' : 'All products'}
          </h2>
          <p className="mt-1 text-sm text-muted">{products.length} styles</p>
          <ul className="mt-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => (
              <ProductCard key={product.product_id} product={product} />
            ))}
          </ul>
        </>
      )}
    </div>
  )
}
