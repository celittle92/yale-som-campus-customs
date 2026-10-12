import { Link } from 'react-router-dom'

const categories = [
  { label: 'Crewneck sweatshirts', note: 'The one you reach for in October.' },
  { label: 'Hoodies', note: 'Pullover and full-zip, light to heavyweight.' },
  { label: 'T-shirts', note: 'Short sleeve, including The Game designs.' },
  { label: 'Quarter-zips', note: 'Layerable, and the closest thing to business casual.' },
  { label: 'Fleece and jackets', note: 'For when New Haven turns on you in November.' },
]

const collections = [
  {
    title: 'Your residential college',
    body: 'Benjamin Franklin, Berkeley, Branford, Davenport, Grace Hopper, Jonathan Edwards, Morse, Pierson, Saybrook, Timothy Dwight and more, on quarter-zips, crewnecks and tees.',
  },
  {
    title: 'Your team',
    body: 'Baseball, football, hockey, soccer, lacrosse, crew, tennis and field hockey, mostly as left-chest logos rather than full-front graphics.',
  },
  {
    title: 'Your school',
    body: 'Law, Medicine, Management, Nursing, Divinity, Architecture, Art, Music, Engineering and Public Health.',
  },
]

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-12">
      <section className="max-w-3xl">
        <p className="text-sm font-semibold tracking-widest text-accent uppercase">
          Officially licensed Yale apparel
        </p>
        <h1 className="mt-3 font-display text-4xl leading-tight font-bold text-ink sm:text-5xl">
          Yale gear that holds up, from a shop two blocks from campus.
        </h1>
        <p className="mt-5 text-lg leading-relaxed text-body">
          We stock 102 styles right now — sweatshirts, hoodies, tees, quarter-zips and
          jackets, in sizes XS through XXL, from $32 to $98. Everything on this site is
          what we actually have, and if a size is out, we say so on the page instead of
          letting you find out at checkout.
        </p>
        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            to="/products"
            className="rounded bg-accent px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ink"
          >
            Browse all 102 styles
          </Link>
          <Link
            to="/about"
            className="rounded border border-line px-5 py-3 text-sm font-semibold text-ink transition-colors hover:bg-accent-soft"
          >
            About the shop
          </Link>
        </div>
      </section>

      <section className="mt-16" aria-labelledby="what-we-carry">
        <h2 id="what-we-carry" className="font-display text-2xl font-bold text-ink">
          What we carry
        </h2>
        <ul className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.map((category) => (
            <li
              key={category.label}
              className="rounded-lg border border-line bg-paper p-5"
            >
              <h3 className="font-semibold text-ink">{category.label}</h3>
              <p className="mt-1 text-sm leading-relaxed text-body">{category.note}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-16" aria-labelledby="find-yours">
        <h2 id="find-yours" className="font-display text-2xl font-bold text-ink">
          Find the one that is actually yours
        </h2>
        <p className="mt-2 max-w-2xl text-body">
          Most people come in knowing roughly what they want and leave with something
          specific. These are the three ways that usually happens.
        </p>
        <div className="mt-6 grid gap-5 md:grid-cols-3">
          {collections.map((collection) => (
            <article
              key={collection.title}
              className="rounded-lg border border-line bg-paper p-6"
            >
              <h3 className="font-display text-lg font-semibold text-ink">
                {collection.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-body">{collection.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="mt-16 rounded-lg border border-line bg-accent-soft p-8">
        <h2 className="font-display text-2xl font-bold text-ink">
          Not sure what you are looking for?
        </h2>
        <p className="mt-2 max-w-2xl leading-relaxed text-body">
          Use the chat in the bottom corner. It reads the same catalogue this site does,
          so it can tell you what a style costs and which sizes are left — and it will
          tell you when it does not know rather than guessing.
        </p>
      </section>
    </div>
  )
}
