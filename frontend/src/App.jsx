import { useState } from 'react'
import { lookupBook, saveBook } from './services/api'
import './styles/App.css'

function App() {
  const [query, setQuery] = useState('')
  const [books, setBooks] = useState([])
  const [page, setPage] = useState(1)
  const [selectedBook, setSelectedBook] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const fetchBooks = async (searchQuery, pageNum = 1) => {
    if (!searchQuery.trim()) return
    setLoading(true)
    setError('')
    setSelectedBook(null)
    try {
      const data = await lookupBook(searchQuery, pageNum)
      setBooks(data)
      setPage(pageNum)
      if (data.length === 0) {
        setError(pageNum === 1 ? 'No books found.' : 'No more books found.')
      }
    } catch (err) {
      setError('Failed to fetch books.')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    await fetchBooks(query, 1)
  }

  // When user selects a book, save it to PostgreSQL cache!
  const handleSelectBook = async (book) => {
    try {
      const saved = await saveBook(book)
      setSelectedBook(saved)
      // Update book in list so its status changes to cached
      setBooks((prev) =>
        prev.map((b) => (b.isbn === book.isbn ? { ...b, id: saved.id } : b))
      )
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
      
      {/* Search Results */}
      {books.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0 }}>Results (Page {page}):</h3>
            <span style={{ fontSize: 13, color: '#666' }}>Showing {books.length} items</span>
          </div>
          <div style={{ display: 'grid', gap: 12, marginTop: 12 }}>
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
                  disabled={Boolean(b.id)}
                  style={{
                    padding: '8px 14px',
                    background: b.id ? '#10b981' : '#2563eb',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 6,
                    cursor: b.id ? 'default' : 'pointer'
                  }}
                >
                  {b.id ? '✓ Cached' : 'Select & Cache'}
                </button>
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16 }}>
            <button
              onClick={() => fetchBooks(query, page - 1)}
              disabled={page <= 1 || loading}
              style={{ padding: '8px 16px', cursor: page <= 1 ? 'not-allowed' : 'pointer' }}
            >
              ← Previous
            </button>
            <span style={{ fontWeight: 'bold', color: '#555' }}>Page {page}</span>
            <button
              onClick={() => fetchBooks(query, page + 1)}
              disabled={books.length < 5 || loading}
              style={{ padding: '8px 16px', cursor: books.length < 5 ? 'not-allowed' : 'pointer' }}
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
export default App