import {describe, it, expect, vi} from 'vitest'
import { lookupBook } from '../services/api'

describe('Book API Service', () => {
    it('lookupBook calls the correct URL and returns JSON', async () => {
        // Mock browser fetch function
        const mockBookData = { title: 'Dune', author_name: 'Frank Herbert', isbn: '123' }

        globalThis.fetch = vi.fn().mockResolvedValue({
            ok: true, 
            json: async () => mockBookData,
        })

    //call lookupBook
    const result = await lookupBook('Dune')

    //assertions (like assert in pytest)
    expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/books/lookup?q=Dune')
    )
    expect(result.title).toBe('Dune')
    expect(result.author_name).toBe('Frank Herbert')
    })
})