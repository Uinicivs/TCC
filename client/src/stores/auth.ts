import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { jwtDecode } from 'jwt-decode'

interface DecodedToken {
  email?: string
  sub?: string
  exp?: number
  [key: string]: unknown
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => {
    return !!accessToken.value
  })

  const userEmail = computed(() => {
    if (!accessToken.value) return null
    try {
      const decoded = jwtDecode<DecodedToken>(accessToken.value)
      return decoded?.email || decoded?.sub || null
    } catch {
      return null
    }
  })

  const userInitials = computed(() => {
    if (!userEmail.value) return '?'
    const email = userEmail.value
    const firstChar = email.charAt(0).toUpperCase()
    return firstChar
  })

  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_expires')
    localStorage.removeItem('auth_token')
  }

  const updateAccessToken = (token: string) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  return {
    accessToken,
    refreshToken,
    isAuthenticated,
    userEmail,
    userInitials,
    setTokens,
    clearTokens,
    updateAccessToken,
  }
})
