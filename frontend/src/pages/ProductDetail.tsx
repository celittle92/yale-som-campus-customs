import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice } from '../api'
import type { ProductDetail as Detail } from '../types'

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>()
  const [product, setProduct] = useState<Detail | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!productId) return
    let active = true
    setProduct(null)
    setError(null)
    fetchProduct(productId)
      .then((data) => active && setProduct(data))
      .catch((caught: Error) => active && setError(caught.message))
    return () => {
      active = false
    }
  }, [productId])

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-5 py-16">
        <p role="alert" className="text-lg text-ink">
          {error}
        </p>
        <Link to="/products" className="mt-4 inline-block text-accent underline">
          Back to all products
        </Link>
      </div>
    )
  }

  if (!product) {
    return <p className="mx-auto max-w-6xl px-5 py-16 text-muted">Loading…</p>
  }

  const available = product.sizes.filter((size) => size.in_stock)

  return (
    <div className="mx-auto max-w-6xl px-5 py-10">
      <Link to="/products" className="text-sm text-accent hover:underline">
        &larr; All products
      </Link>

      <div className="mt-6 grid gap-10 lg:grid-cols-2">
        {/* Large image on the left, full product text on the right. */}
        <div className="overflow-hidden rounded-lg border border-line bg-paper">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full object-cover"
          />
        </div>

        <div>
          <h1 className="font-display text-3xl leading-tight font-bold text-ink">
            {product.name}
          </h1>
          <p className="mt-2 text-sm text-muted capitalize">{product.garment_type}</p>

          <p className="mt-5 text-2xl font-semibold text-accent">
            {formatPrice(product.price)}
          </p>

          <p className="mt-5 leading-relaxed text-body">{product.description}</p>

          <section className="mt-8" aria-labelledby="colors-heading">
            <h2 id="colors-heading" className="text-sm font-semibold text-ink">
              Colours
            </h2>
            {product.colors.length > 0 ? (
              <ul className="mt-2 flex flex-wrap gap-2">
                {product.colors.map((color) => (
                  <li
                    key={color}
                    className="rounded-full border border-line bg-paper px-3 py-1 text-sm text-body capitalize"
                  >
                    {color}
                  </li>
                ))}
              </ul>
            ) : (
              /* Three catalogue products have an empty colors array. Say so rather
                 than inferring a colour from the description or the photo. */
              <p className="mt-2 text-sm text-muted">
                We do not have colours recorded for this item. The description and photo
                are the best guide, or ask us in the shop.
              </p>
            )}
          </section>

          <section className="mt-8" aria-labelledby="sizes-heading">
            <h2 id="sizes-heading" className="text-sm font-semibold text-ink">
              Sizes and stock
            </h2>
            {product.sizes.length > 0 ? (
              <>
                <ul className="mt-3 flex flex-wrap gap-2">
                  {product.sizes.map((size) => (
                    <li
                      key={size.size}
                      className={
                        size.in_stock
                          ? 'rounded border border-line bg-paper px-4 py-2 text-sm font-medium text-ink'
                          : 'rounded border border-line bg-cream px-4 py-2 text-sm text-muted line-through'
                      }
                      title={
                        size.in_stock
                          ? `${size.quantity} in stock`
                          : 'Out of stock in this size'
                      }
                    >
                      {size.size}
                      <span className="ml-2 text-xs font-normal">
                        {size.in_stock ? `${size.quantity} left` : 'out'}
                      </span>
                    </li>
                  ))}
                </ul>
                <p className="mt-3 text-sm text-body">
                  {available.length === 0
                    ? 'Out of stock in every size right now.'
                    : `In stock in ${available.length} of ${product.sizes.length} sizes.`}
                </p>
              </>
            ) : (
              <p className="mt-2 text-sm text-muted">
                We do not have stock recorded for this item.
              </p>
            )}
          </section>

          {product.search_tags.length > 0 && (
            <section className="mt-8" aria-labelledby="tags-heading">
              <h2 id="tags-heading" className="text-sm font-semibold text-ink">
                Details
              </h2>
              <ul className="mt-2 flex flex-wrap gap-2">
                {product.search_tags.map((tag) => (
                  <li key={tag} className="text-xs text-muted">
                    {tag}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
