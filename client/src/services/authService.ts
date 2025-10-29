import api from './api'
import { useAuthStore } from '@/stores/auth'
import type {
  ILoginPayload,
  ILoginResponse,
  IRegisterPayload,
  IRegisterResponse,
} from '@/interfaces/auth'

export const login = async (payload: ILoginPayload): Promise<ILoginResponse> => {
  try {
    const response = await api.post<ILoginResponse>('/auth/login', payload)

    const authStore = useAuthStore()
    authStore.setTokens(response.data.accessToken, response.data.refreshToken)

    localStorage.setItem('token_expires', response.data.tokenExpires)

    return response.data
  } catch {
    throw new Error('Falha ao fazer login. Verifique suas credenciais.')
  }
}

export const register = async (payload: IRegisterPayload): Promise<IRegisterResponse> => {
  try {
    const response = await api.post<IRegisterResponse>('/users', payload)
    return response.data
  } catch {
    throw new Error('Falha ao criar conta. Tente novamente.')
  }
}

export const logout = (): void => {
  const authStore = useAuthStore()
  authStore.clearTokens()
}
