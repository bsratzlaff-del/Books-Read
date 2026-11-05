import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import App from '../App'
import * as api from '../services/api'

describe('<App /> Component', () => {
  it('renders the search bar and heading', () => {
    render(<App />)
    
    // Verify initial UI elements
    expect(screen.getByText('📚 Book Cache Finder')).toBeTruthy()
    expect(screen.getByPlaceholderText(/search by title or author/i)).toBeTruthy()
    expect(screen.getByRole('button', { name: /search/i })).toBeTruthy()
  })

  it('searches for a book and displays the result on screen', async () => {
    // 1. Mock the lookupBook API service (now returns an array of results)
    vi.spyOn(api, 'lookupBook').mockResolvedValue([
      {
        title: 'Dune',
        author_name: 'Frank Herbert',
        isbn: '9780441172719',
      },
    ])

    render(<App />)

    // 2. Simulate typing into the search input
    const input = screen.getByPlaceholderText(/search by title or author/i)
    fireEvent.change(input, { target: { value: 'Dune' } })

    // 3. Simulate clicking the search button
    const button = screen.getByRole('button', { name: /search/i })
    fireEvent.click(button)

    // 4. Wait for the book title to appear on the screen!
    await waitFor(() => {
      expect(screen.getByText('Dune')).toBeTruthy()
      expect(screen.getByText(/Frank Herbert/)).toBeTruthy()
    })
  })
})