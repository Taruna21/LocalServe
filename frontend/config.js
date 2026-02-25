// All API URLs in one place
// Change this one line when you deploy to production
const API_BASE = 'http://127.0.0.1:8000/api'
const WS_BASE  = 'ws://127.0.0.1:8000/ws'

// Helper — get token from localStorage
const getToken = () => localStorage.getItem('access_token')

// Helper — auth headers for fetch calls
const authHeaders = () => ({
    'Content-Type':  'application/json',
    'Authorization': `Bearer ${getToken()}`
})