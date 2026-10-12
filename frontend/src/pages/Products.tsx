import { useEffect, useState } from 'react'
import ProductCard from '../components/ProductCard'
import { fetchProducts } from '../api'
import type { ProductSummary } from '../types'

export default function Products() {
  const [products, setProducts] = useState<ProductSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)

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

      {error && (
        <p
          role="alert"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 px-5 py-4 text-red-800"
        >
          {error} Check that the backend is running on port 8000.
        </p>
      )}

      {!products && !error && (
        <p className="mt-8 text-muted">Loading the catalogue…</p>
      )}

      {products && (
        <>
          <p className="mt-8 text-sm text-muted">{products.length} styles</p>
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
