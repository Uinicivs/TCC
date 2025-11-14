import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { IUser } from '@/interfaces/user'
import { getUserData } from '@/services/user'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<IUser | null>(null)

  const isAuthenticated = computed(() => {
    return !!accessToken.value
  })

  const userEmail = computed(() => {
    return user.value?.email || null
  })

  const userName = computed(() => {
    return user.value?.name || null
  })

  const userInitials = computed(() => {
    if (!user.value?.name) return '?'
    const nameParts = user.value.name.split(' ')
    if (nameParts.length >= 2) {
      return (nameParts[0].charAt(0) + nameParts[1].charAt(0)).toUpperCase()
    }
    return user.value.name.charAt(0).toUpperCase()
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
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_expires')
    localStorage.removeItem('auth_token')
  }

  const updateAccessToken = (token: string) => {
    accessToken.value = token
    localStorage.setItem('access_token', token)
  }

  const fetchUserData = async () => {
    try {
      user.value = await getUserData()
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error)
      throw error
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    userEmail,
    userName,
    userInitials,
    setTokens,
    clearTokens,
    updateAccessToken,
    fetchUserData,
  }
})
