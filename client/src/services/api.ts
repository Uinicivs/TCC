import axios, { AxiosError } from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(({ reject, resolve }) => {
    if (error) {
      reject(error)
      return
    }
    resolve(token)
  })

  failedQueue = []
}

api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  },
)

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    if (error.response?.status !== 401 || !originalRequest) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject })
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
        .catch((err) => {
          return Promise.reject(err)
        })
    }

    originalRequest._retry = true
    isRefreshing = true

    const authStore = useAuthStore()
    const refresh = authStore.refreshToken

    if (!refresh) {
      isRefreshing = false
      processQueue(new Error('No refresh token available'), null)
      return Promise.reject(error)
    }

    try {
      const refreshResponse = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/auth/refresh?refresh_token=${refresh}`,
        { headers: { 'Content-Type': 'application/json' } },
      )

      const { accessToken } = refreshResponse.data

      authStore.updateAccessToken(accessToken)

      originalRequest.headers.Authorization = `Bearer ${accessToken}`
      isRefreshing = false
      processQueue(null, accessToken)
      return api(originalRequest)
    } catch (err) {
      isRefreshing = false
      processQueue(err as Error, null)
      return Promise.reject(err)
    }
  },
)

export default api
