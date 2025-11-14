import api from './api'
import { useAuthStore } from '@/stores/auth'
import type { ILoginPayload, ILoginResponse } from '@/interfaces/auth'

export const login = async (payload: ILoginPayload): Promise<ILoginResponse> => {
  try {
    const response = await api.post<ILoginResponse>('/auth/login', payload)

    const authStore = useAuthStore()
    authStore.setTokens(response.data.accessToken, response.data.refreshToken)

    localStorage.setItem('token_expires', response.data.tokenExpires)

    await authStore.fetchUserData()

    return response.data
  } catch {
    throw new Error('Falha ao fazer login. Verifique suas credenciais.')
  }
}

export const logout = (): void => {
  const authStore = useAuthStore()
  authStore.clearTokens()
}
