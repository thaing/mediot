import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getStoredToken, logout as authLogout } from '../services/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getStoredToken())
  const user = ref(null)

  const userJson = localStorage.getItem('user')
  if (userJson) {
    try {
      user.value = JSON.parse(userJson)
    } catch {}
  }

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => {
    if (user.value?.first_name || user.value?.last_name) {
      return `${user.value.first_name || ''} ${user.value.last_name || ''}`.trim()
    }
    return user.value?.email || 'User'
  })

  function login(newToken, newUser) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('access_token', newToken)
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    }
  }

  function logout() {
    token.value = null
    user.value = null
    authLogout()
  }

  return { token, user, isAuthenticated, userName, login, logout }
})
