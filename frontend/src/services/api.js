
const BOOK_CACHE_URL = import.meta.env.VITE_BOOK_CACHE_URL || 'http://localhost:8000';
const USERS_BACKEND_URL = import.meta.env.VITE_USERS_BACKEND_URL || 'http://localhost:8001';

//get lookup book public
export async function lookupBook(query) {
    const res = await fetch(`${BOOK_CACHE_URL}/books/lookup?q=${encodeURIComponent(query)}`);
    return res.json();
}

//get user library public
export async function getUserLibrary(userID) {
    const res = await fetch(`${USERS_BACKEND_URL}/users/${userID}/books`);
    return res.json();
}