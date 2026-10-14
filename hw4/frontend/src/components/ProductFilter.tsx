import { useMemo } from 'react'
import type { ProductSummary } from '../types'

export type Filters = {
  type: string
  color: string
  size: string
  /** 'college' | 'team' | 'school' — the three ways people actually shop. */
  theme: string
  inStockOnly: boolean
}

export const EMPTY_FILTERS: Filters = {
  type: '',
  color: '',
  size: '',
  theme: '',
  inStockOnly: false,
}

export const THEME_LABELS: Record<string, string> = {
  college: 'Residential colleges',
  team: 'Varsity teams',
  school: 'Graduate schools',
}

export const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

// The same seven labels the backend uses (tools.CATEGORY_RULES). Kept in the same order
// so the two never disagree about what a category is called.
const CATEGORY_RULES: [string, string[]][] = [
  ['Fleece jacket', ['fleece jacket']],
  ['Jacket', ['bomber jacket', 'jacket']],
  ['Quarter-zip', ['quarter-zip', 'quarter zip', '1/4 zip']],
  ['Hoodie', ['hoodie', 'hooded']],
  ['Crewneck sweatshirt', ['crewneck', 'mockneck']],
  ['Long-sleeve shirt', ['long-sleeve performance', 'long sleeve performance']],
  ['T-shirt', ['t-shirt', 'tee']],
]

export function categoryOf(garmentType: string): string {
  const lowered = garmentType.toLowerCase()
  for (const [label, keywords] of CATEGORY_RULES) {
    if (keywords.some((k) => lowered.includes(k))) return label
  }
  return 'Other'
}

export const CATEGORIES = CATEGORY_RULES.map(([label]) => label)

/**
 * Filtering runs in the browser over the already-loaded catalogue, so it is instant and
 * costs nothing. Size and stock need per-product inventory, which the list endpoint does
 * not carry, so those two are applied against a stock map the page loads once.
 */
export function applyFilters(
  products: ProductSummary[],
  filters: Filters,
  stockBySize: Record<string, Record<string, number>>,
): ProductSummary[] {
  return products.filter((product) => {
    if (filters.type && categoryOf(product.garment_type) !== filters.type) return false
    if (filters.theme && !(product.themes ?? []).includes(filters.theme)) return false
    if (
      filters.color &&
      !product.colors.some((c) => c.toLowerCase() === filters.color.toLowerCase())
    ) {
      return false
    }

    const stock = stockBySize[product.product_id]
    if (filters.size) {
      if (!stock) return true // stock not loaded yet; do not hide it wrongly
      // Picking a size you cannot buy is the disappointment this filter exists to stop,
      // so a chosen size always means "in stock in that size".
      if ((stock[filters.size] ?? 0) <= 0) return false
    } else if (filters.inStockOnly) {
      if (!stock) return true
      if (!Object.values(stock).some((q) => q > 0)) return false
    }
    return true
  })
}

type Props = {
  products: ProductSummary[]
  filters: Filters
  onChange: (filters: Filters) => void
  matchCount: number
}

export default function ProductFilter({
  products,
  filters,
  onChange,
  matchCount,
}: Props) {
  // Colours come from the catalogue rather than a hard-coded list, so the control can
  // never offer a colour we do not sell.
  const colors = useMemo(() => {
    const seen = new Set<string>()
    products.forEach((p) => p.colors.forEach((c) => seen.add(c.toLowerCase())))
    return [...seen].sort()
  }, [products])

  const active =
    filters.type || filters.color || filters.size || filters.theme || filters.inStockOnly

  const select =
    'mt-1 w-full cursor-pointer rounded border border-line bg-paper px-3 py-2 text-sm text-ink'

  return (
    <section
      aria-labelledby="filter-heading"
      className="mt-8 rounded-lg border border-line bg-paper p-5"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h2 id="filter-heading" className="font-display text-lg font-semibold text-ink">
          Filter
        </h2>
        <p className="text-sm text-body" aria-live="polite">
          {matchCount} of {products.length} styles
        </p>
      </div>

      {filters.theme && (
        <p className="mt-3 flex flex-wrap items-center gap-2 text-sm text-body">
          Showing
          <span className="inline-flex items-center gap-2 rounded-full bg-accent-soft px-3 py-1 text-sm font-semibold text-accent">
            {THEME_LABELS[filters.theme] ?? filters.theme}
            <button
              type="button"
              aria-label={`Remove the ${THEME_LABELS[filters.theme] ?? filters.theme} filter`}
              onClick={() => onChange({ ...filters, theme: '' })}
              className="cursor-pointer text-accent/70 transition-colors hover:text-accent"
            >
              ✕
            </button>
          </span>
        </p>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label htmlFor="filter-type" className="block text-sm font-medium text-ink">
            Type
          </label>
          <select
            id="filter-type"
            className={select}
            value={filters.type}
            onChange={(e) => onChange({ ...filters, type: e.target.value })}
          >
            <option value="">Any type</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="filter-color" className="block text-sm font-medium text-ink">
            Colour
          </label>
          <select
            id="filter-color"
            className={`${select} capitalize`}
            value={filters.color}
            onChange={(e) => onChange({ ...filters, color: e.target.value })}
          >
            <option value="">Any colour</option>
            {colors.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="filter-size" className="block text-sm font-medium text-ink">
            Size
          </label>
          <select
            id="filter-size"
            className={select}
            value={filters.size}
            onChange={(e) => onChange({ ...filters, size: e.target.value })}
          >
            <option value="">Any size</option>
            {SIZES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          {filters.size && (
            <p className="mt-1 text-xs text-muted">Only showing items in stock in {filters.size}.</p>
          )}
        </div>

        <div className="flex flex-col justify-end gap-2">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={filters.inStockOnly}
              disabled={!!filters.size}
              onChange={(e) => onChange({ ...filters, inStockOnly: e.target.checked })}
              className="h-4 w-4 cursor-pointer accent-[var(--color-accent)] disabled:cursor-not-allowed"
            />
            Exclude out of stock
          </label>
          {active && (
            <button
              type="button"
              onClick={() => onChange(EMPTY_FILTERS)}
              className="cursor-pointer self-start text-sm text-accent underline"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>
    </section>
  )
}
