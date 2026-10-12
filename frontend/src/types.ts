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
  products: ProductSummary[]
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
