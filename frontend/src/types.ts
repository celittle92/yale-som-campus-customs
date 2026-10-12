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
