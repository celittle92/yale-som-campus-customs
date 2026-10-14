import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './AuthContext'
import { ChatProvider } from './ChatContext'
import ChatPanel from './components/ChatPanel'
import NavBar from './components/NavBar'
import About from './pages/About'
import CreateAccount from './pages/CreateAccount'
import Home from './pages/Home'
import LogIn from './pages/LogIn'
import ProductDetail from './pages/ProductDetail'
import Products from './pages/Products'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ChatProvider>
        <div className="flex min-h-screen flex-col bg-cream">
        <NavBar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<Products />} />
            <Route path="/products/:productId" element={<ProductDetail />} />
            <Route path="/about" element={<About />} />
            <Route path="/login" element={<LogIn />} />
            <Route path="/create-account" element={<CreateAccount />} />
            <Route
              path="*"
              element={
                <p className="mx-auto max-w-3xl px-5 py-16 text-ink">
                  That page does not exist.
                </p>
              }
            />
          </Routes>
        </main>
        <footer className="border-t border-line bg-paper">
          <div className="mx-auto max-w-6xl px-5 py-8 text-sm text-muted">
            Campus Customs · 57 Broadway, New Haven, Connecticut · Officially licensed
            Yale apparel
          </div>
        </footer>
          <ChatPanel />
          </div>
        </ChatProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
