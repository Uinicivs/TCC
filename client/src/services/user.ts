import api from './api'
import type { IUser } from '@/interfaces/user'

export const getUserData = async (): Promise<IUser> => {
  try {
    const response = await api.get<IUser>('/users/me')
    return response.data
  } catch {
    throw new Error('Falha ao buscar os dados do usuário. Tente novamente.')
  }
}
