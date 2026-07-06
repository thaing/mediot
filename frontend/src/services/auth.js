const API_BASE = '/api/v1'

export function initOAuthLogin(provider) {
  window.location.href = `${API_BASE}/auth/login/${provider}`
}

export function handleOAuthCallback() {
  const params = new URLSearchParams(window.location.hash.substring(1))
  const token = params.get('access_token')
  const userJson = params.get('user')

  if (!token) {
    const searchParams = new URLSearchParams(window.location.search)
    const queryToken = searchParams.get('access_token')
    const queryUser = searchParams.get('user')
    if (queryToken) {
      console.log('[OAuth] Found token in URL query params')
      localStorage.setItem('access_token', queryToken)
      if (queryUser) {
        localStorage.setItem('user', queryUser)
        console.log('[OAuth] Stored user data in localStorage')
      }
      return { token: queryToken, user: queryUser ? JSON.parse(decodeURIComponent(queryUser)) : null }
    }
    console.log('[OAuth] No token found in URL')
    return null
  }

  localStorage.setItem('access_token', token)
  if (userJson) {
    localStorage.setItem('user', userJson)
  }
  return { token, user: userJson ? JSON.parse(decodeURIComponent(userJson)) : null }
}

export function getStoredToken() {
  return localStorage.getItem('access_token')
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  window.location.href = '/login'
}
