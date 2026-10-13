import { Link } from 'react-router-dom'

const categories = [
  { label: 'Crewneck sweatshirts', note: 'The one you reach for in October.', count: 29 },
  { label: 'Hoodies', note: 'Pullover and full-zip, light to heavyweight.', count: 27 },
  { label: 'T-shirts', note: 'Short sleeve, including The Game designs.', count: 25 },
  { label: 'Quarter-zips', note: 'The closest thing to business casual.', count: 11 },
  { label: 'Fleece and jackets', note: 'For when New Haven turns on you.', count: 8 },
]

const collections = [
  {
    title: 'Your residential college',
    body: 'Benjamin Franklin, Berkeley, Branford, Davenport, Grace Hopper, Jonathan Edwards, Morse, Pierson, Saybrook, Timothy Dwight and more.',
  },
  {
    title: 'Your team',
    body: 'Baseball, football, hockey, soccer, lacrosse, crew, tennis and field hockey, mostly as left-chest logos.',
  },
  {
    title: 'Your school',
    body: 'Law, Medicine, Management, Nursing, Divinity, Architecture, Art, Music, Engineering and Public Health.',
  },
]

// Real catalogue photography, so the hero shows what the shop actually sells.
const heroImages = [
  { id: 'basic-hoodie-big-yale', label: 'Basic Hoodie Big Yale' },
  { id: '2025-yale-vs-harvard-t-shirt', label: '2025 Yale vs Harvard T-Shirt' },
  { id: 'benjamin-franklin-fleece-jacket', label: 'Benjamin Franklin Fleece Jacket' },
]

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-14">
      {/* Hero: words on the left, the goods on the right. */}
      <section className="grid items-center gap-12 lg:grid-cols-[1.05fr_1fr]">
        <div className="animate-rise">
          <p className="inline-flex items-center gap-2 rounded-full border border-line bg-paper px-3 py-1 text-xs font-medium tracking-[0.14em] text-accent uppercase">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            Officially licensed Yale apparel
          </p>
          <h1 className="mt-6 font-display text-[2.75rem] leading-[1.05] font-bold text-ink sm:text-6xl">
            Yale gear that holds&nbsp;up,
            <span className="block text-accent">two blocks from campus.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-body">
            102 styles in stock — sweatshirts, hoodies, tees, quarter-zips and jackets,
            XS through XXL, $32 to $98. If your size is gone, the page says so before you
            get attached to it.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/products"
              className="group rounded-full bg-accent px-6 py-3.5 text-sm font-semibold text-white shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:bg-accent-deep hover:shadow-lift"
            >
              Browse all 102 styles
              <span className="ml-2 inline-block transition-transform duration-300 group-hover:translate-x-1">
                →
              </span>
            </Link>
            <Link
              to="/about"
              className="rounded-full border border-line bg-paper px-6 py-3.5 text-sm font-semibold text-ink transition-all duration-300 hover:-translate-y-0.5 hover:border-accent hover:shadow-card"
            >
              About the shop
            </Link>
          </div>
        </div>

        {/* Offset collage — the tallest piece leads, the others step down. */}
        <div className="animate-rise grid grid-cols-2 gap-4 [animation-delay:120ms]">
          <Link
            to={`/products/${heroImages[0].id}`}
            className="group relative col-span-1 row-span-2 overflow-hidden rounded-2xl border border-line bg-sand shadow-card transition-all duration-500 hover:-translate-y-1 hover:shadow-lift"
          >
            <img
              src={`/api/products/${heroImages[0].id}/image`}
              alt={heroImages[0].label}
              className="h-full w-full object-cover object-top transition-transform duration-700 ease-[var(--ease-out-soft)] group-hover:scale-105"
            />
          </Link>
          {heroImages.slice(1).map((item, i) => (
            <Link
              key={item.id}
              to={`/products/${item.id}`}
              className="group relative overflow-hidden rounded-2xl border border-line bg-sand shadow-card transition-all duration-500 hover:-translate-y-1 hover:shadow-lift"
              style={{ marginTop: i === 0 ? '1.25rem' : undefined }}
            >
              <img
                src={`/api/products/${item.id}/image`}
                alt={item.label}
                className="aspect-square h-full w-full object-cover transition-transform duration-700 ease-[var(--ease-out-soft)] group-hover:scale-105"
              />
            </Link>
          ))}
        </div>
      </section>

      {/* A thin band of facts, which reads as a shop that knows its own stock. */}
      <section className="mt-20 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-4">
        {[
          ['102', 'styles in stock'],
          ['XS–XXL', 'every item, six sizes'],
          ['$32–$98', 'no hidden pricing'],
          ['57 Broadway', 'New Haven'],
        ].map(([big, small]) => (
          <div key={small} className="bg-paper px-6 py-7">
            <p className="font-display text-2xl font-semibold text-ink">{big}</p>
            <p className="mt-1 text-sm text-body">{small}</p>
          </div>
        ))}
      </section>

      <section className="mt-20" aria-labelledby="what-we-carry">
        <h2 id="what-we-carry" className="font-display text-3xl font-bold text-ink">
          What we carry
        </h2>
        <ul className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((category, i) => (
            <li
              key={category.label}
              className="animate-rise group rounded-xl border border-line bg-paper p-6 transition-all duration-300 hover:-translate-y-0.5 hover:border-accent/30 hover:shadow-card"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="flex items-baseline justify-between gap-3">
                <h3 className="font-display text-lg font-semibold text-ink">
                  {category.label}
                </h3>
                <span className="rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-semibold text-accent">
                  {category.count}
                </span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-body">{category.note}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-20" aria-labelledby="find-yours">
        <h2 id="find-yours" className="font-display text-3xl font-bold text-ink">
          Find the one that is actually yours
        </h2>
        <p className="mt-2 max-w-2xl text-body">
          Most people come in knowing roughly what they want and leave with something
          specific. These are the three ways that usually happens.
        </p>
        <div className="mt-7 grid gap-5 md:grid-cols-3">
          {collections.map((collection, i) => (
            <article
              key={collection.title}
              className="animate-rise relative overflow-hidden rounded-xl border border-line bg-paper p-6 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-card"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <span
                aria-hidden="true"
                className="absolute top-0 left-0 h-full w-1 bg-accent/80"
              />
              <h3 className="font-display text-lg font-semibold text-ink">
                {collection.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-body">{collection.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-20 overflow-hidden rounded-2xl bg-accent px-8 py-12 text-white sm:px-12">
        <h2 className="font-display text-3xl font-bold">
          Not sure what you are looking for?
        </h2>
        <p className="mt-3 max-w-2xl leading-relaxed text-white/85">
          Use the chat in the bottom corner. It reads the same catalogue this site does,
          so it can tell you what a style costs and which sizes are left — and it will
          tell you when it does not know rather than guessing.
        </p>
      </section>
    </div>
  )
}
