export type ProductSummary = {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
}

export type SizeStock = {
  size: string
  quantity: number
  in_stock: boolean
}

export type ProductDetail = ProductSummary & {
  search_tags: string[]
  sizes: SizeStock[]
}

export type ChatReply = {
  reply: string
  /** Whole catalogue rows, resolved by the backend from the ids the agent returned. */
  products: ProductSummary[]
  /** Short heading for the set, e.g. "Hoodies". Null when there are no products. */
  match_label: string | null
  /** True when the exchange was saved to chat_messages, i.e. the shopper is signed in. */
  saved: boolean
}

/** What the backend is willing to say about a user. Never includes the password hash. */
export type PublicUser = {
  id: number
  first_name: string | null
  last_name: string | null
  name: string
  email: string
}

export type SignupInput = {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

/** One stored turn, as the panel re-renders it for a returning shopper. */
export type ChatHistoryMessage = {
  role: 'user' | 'assistant'
  content: string
  products: ProductSummary[]
  created_at: string
}
