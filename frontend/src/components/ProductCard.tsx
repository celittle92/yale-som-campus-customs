import { Link } from 'react-router-dom'
import { formatPrice } from '../api'
import type { ProductSummary } from '../types'

export default function ProductCard({ product }: { product: ProductSummary }) {
  return (
    <li>
      {/* The whole card is one link, so the image, the name and the price are all the
          same target rather than three separate tab stops. */}
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
        <div className="flex flex-1 flex-col gap-2 p-4">
          <h3 className="font-display text-lg leading-snug font-semibold text-ink">
            {product.name}
          </h3>
          <p className="line-clamp-3 flex-1 text-sm leading-relaxed text-body">
            {product.description}
          </p>
          <div className="flex items-baseline justify-between pt-1">
            <span className="text-base font-semibold text-accent">
              {formatPrice(product.price)}
            </span>
            <span className="text-xs text-muted capitalize">
              {product.garment_type}
            </span>
          </div>
        </div>
      </Link>
    </li>
  )
}
