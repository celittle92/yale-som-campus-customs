import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, fetchSimilar, formatPrice } from '../api'
import ProductRow from '../components/ProductRow'
import { recordGuestView } from '../recentlyViewed'
import { useChat } from '../ChatContext'
import type { ProductDetail as Detail, ProductSummary } from '../types'

type ProductSummaryList = ProductSummary[]

export default function ProductDetail() {
  const { productId } = useParams<{ productId: string }>()
  const [product, setProduct] = useState<Detail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedSize, setSelectedSize] = useState<string | null>(null)
  const [similar, setSimilar] = useState<Detail[] | ProductSummaryList>([])
  const { openWith } = useChat()

  useEffect(() => {
    if (!productId) return
    let active = true
    setProduct(null)
    setError(null)
    setSelectedSize(null)
    fetchProduct(productId)
      .then((data) => active && setProduct(data))
      .catch((caught: Error) => active && setError(caught.message))

    // Recently viewed. For a signed-in shopper the GET above already recorded it
    // server-side; a guest's list stays in their own browser and is never sent.
    recordGuestView(productId)

    // Recommendations load separately so they never delay the product itself.
    setSimilar([])
    fetchSimilar(productId)
      .then((data) => active && setSimilar(data))
      .catch(() => undefined)

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
  const selected = product.sizes.find((size) => size.size === selectedSize) ?? null

  return (
    <div className="mx-auto max-w-6xl px-5 py-10">
      <Link to="/products" className="text-sm text-accent hover:underline">
        &larr; All products
      </Link>

      <div className="mt-6 grid gap-10 lg:grid-cols-2">
        {/* Large image on the left, full product text on the right. */}
        {/* The image stays put while the details scroll — on a product page the photo
            is the thing you keep referring back to. */}
        <div className="lg:sticky lg:top-24 lg:self-start">
          <div className="group overflow-hidden rounded-2xl border border-line bg-sand shadow-card">
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full object-cover transition-transform duration-700 ease-[var(--ease-out-soft)] group-hover:scale-[1.04]"
            />
          </div>
        </div>

        <div>
          <h1 className="font-display text-4xl leading-[1.1] font-bold text-ink">
            {product.name}
          </h1>
          <p className="mt-2.5 text-xs tracking-[0.12em] text-muted uppercase">
            {product.garment_type}
          </p>

          <p className="mt-6 font-display text-4xl font-semibold text-accent">
            {formatPrice(product.price)}
          </p>

          <p className="mt-6 text-[15px] leading-relaxed text-body">{product.description}</p>

          {/* Colours describe the one garment pictured — `inventory` has no colour
              dimension and there is a single image per product. Rendering these as
              chips made them look selectable, so they read as a sentence instead. */}
          <section className="mt-8" aria-labelledby="colors-heading">
            <h2 id="colors-heading" className="text-sm font-semibold text-ink">
              Colours in this design
            </h2>
            {product.colors.length > 0 ? (
              <p className="mt-2 text-sm text-body">
                <span className="capitalize">{product.colors.join(', ')}</span>. This item
                comes in the one colourway shown.
              </p>
            ) : (
              /* Three catalogue products have an empty colors array. Say so rather
                 than inferring a colour from the description or the photo. */
              /* The three products with no recorded colours are the same three with no
                 written description, so pointing at the description would be useless. */
              <p className="mt-2 text-sm text-muted">
                We do not have colours recorded for this item — the photo is the best
                guide, or ask us in the shop.
              </p>
            )}
          </section>

          <section className="mt-8" aria-labelledby="sizes-heading">
            <h2 id="sizes-heading" className="text-sm font-semibold text-ink">
              Sizes and stock
            </h2>
            {product.sizes.length > 0 ? (
              <>
                {/* Real buttons, not list items: an in-stock size is something you can
                    pick, so it gets a pointer cursor, a pressed state and keyboard
                    focus. Out-of-stock sizes stay visible but disabled. */}
                <div
                  role="group"
                  aria-label="Choose a size"
                  className="mt-3 flex flex-wrap gap-2"
                >
                  {product.sizes.map((size) => {
                    const isSelected = selectedSize === size.size
                    return (
                      <button
                        key={size.size}
                        type="button"
                        disabled={!size.in_stock}
                        aria-pressed={isSelected}
                        aria-label={
                          size.in_stock
                            ? `Size ${size.size}, ${size.quantity} in stock`
                            : `Size ${size.size}, out of stock`
                        }
                        onClick={() =>
                          setSelectedSize(isSelected ? null : size.size)
                        }
                        className={
                          !size.in_stock
                            ? 'cursor-not-allowed rounded-full border border-line bg-sand px-4 py-2 text-sm text-muted line-through'
                            : isSelected
                              ? 'cursor-pointer rounded-full border-2 border-accent bg-accent px-4 py-2 text-sm font-semibold text-white shadow-sm'
                              : 'cursor-pointer rounded-full border border-line bg-paper px-4 py-2 text-sm font-medium text-ink transition-all duration-300 hover:-translate-y-px hover:border-accent hover:bg-accent-soft'
                        }
                      >
                        {size.size}
                        <span className="ml-2 text-xs font-normal">
                          {size.in_stock ? `${size.quantity} left` : 'out'}
                        </span>
                      </button>
                    )
                  })}
                </div>

                <p className="mt-3 text-sm text-body">
                  {available.length === 0
                    ? 'Out of stock in every size right now.'
                    : `In stock in ${available.length} of ${product.sizes.length} sizes.`}
                </p>

                {selected && (
                  <div className="animate-rise mt-4 rounded-xl border border-accent/25 bg-accent-soft p-4">
                    <p className="text-sm text-ink">
                      <span className="font-semibold">Size {selected.size}</span> —{' '}
                      {selected.quantity} in stock.
                    </p>
                    <button
                      type="button"
                      onClick={() =>
                        openWith(
                          `Is the ${product.name} still available in size ${selected.size}?`,
                        )
                      }
                      className="mt-3 cursor-pointer rounded-full bg-accent px-4 py-2 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-px hover:bg-accent-deep"
                    >
                      Ask about size {selected.size}
                    </button>
                  </div>
                )}
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

      {/* You might also like. Similar in type and colour, computed by the backend from
          catalogue data. Out-of-stock items are ranked down, so a recommendation is
          usually something the shopper can actually buy. */}
      <ProductRow
        title="You might also like"
        subtitle="Similar in style and colour to this one."
        products={similar as ProductSummary[]}
      />
    </div>
  )
}
