import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log('[API] 401 received, redirecting to login')
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.replace('/login')
    }
    return Promise.reject(error)
  }
)

export async function fetchReadings(d_id, from_ts, to_ts) {
  const params = { d_id }
  if (from_ts) params.from_ts = from_ts
  if (to_ts) params.to_ts = to_ts
  const res = await api.get('/readings/', { params })
  return res.data
}

export async function fetchDevices() {
  const res = await api.get('/readings/')
  return res.data
}
