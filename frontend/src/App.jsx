import { useState } from 'react'
import { lookupBook } from './services/api'
import './styles/App.css'

function App() {
  const [query, setQuery] = useState('')
  const [book, setBook] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    try {
      const data = await lookupBook(query)
      setBook(data)
    } catch (err) {
      setError('Failed to fetch book.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>📚 Book Cache Finder</h1>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          placeholder="Search book title..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {book && (
        <div style={{ marginTop: 20, padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
          <h2>{book.title}</h2>
          <p><strong>Author:</strong> {book.author_name || 'Unknown'}</p>
          <p><strong>ISBN:</strong> {book.isbn}</p>
        </div>
      )}
    </div>
  )
}

export default App