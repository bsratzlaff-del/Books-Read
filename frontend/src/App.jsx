import { useState } from 'react'
import { lookupBook, saveBook } from './services/api'
import './styles/App.css'

function App() {
  const [query, setQuery] = useState('')
  const [books, setBooks] = useState([])
  const [selectedBook, setSelectedBook] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  

   const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setSelectedBook(null)
    try {
      const data = await lookupBook(query)
      setBooks(data)
      if (data.length === 0) setError('No books found.')
    } catch (err) {
      setError('Failed to fetch books.')
    } finally {
      setLoading(false)
    }
  }

    // When user selects a book, save it to PostgreSQL cache!
  const handleSelectBook = async (book) => {
    try {
      const saved = await saveBook(book)
      setSelectedBook(saved)
      alert(`Saved "${book.title}" to PostgreSQL cache!`)
    } catch (err) {
      alert('Failed to save book.')
    }
  }

  return (
    <div style={{ maxWidth: 650, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>📚 Book Cache Finder</h1>
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          placeholder="Search by title or author (e.g. Dune, Herbert)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{ flex: 1, padding: 8 }}
        />
        <button type="submit" disabled={loading} style={{ padding: '8px 16px' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {/* Top 5 Results */}
      {books.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3>Top Results ({books.length}):</h3>
          <div style={{ display: 'grid', gap: 12 }}>
            {books.map((b, idx) => (
              <div
                key={idx}
                style={{
                  padding: 16,
                  border: '1px solid #ddd',
                  borderRadius: 8,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: '#fafafa'
                }}
              >
                <div>
                  <h4 style={{ margin: '0 0 4px 0' }}>{b.title}</h4>
                  <p style={{ margin: 0, color: '#555' }}>Author: {b.author_name}</p>
                  <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#888' }}>ISBN: {b.isbn}</p>
                </div>
                <button
                  onClick={() => handleSelectBook(b)}
                  style={{
                    padding: '8px 14px',
                    background: '#2563eb',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 6,
                    cursor: 'pointer'
                  }}
                >
                  Select & Cache
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
export default App