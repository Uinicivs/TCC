export interface ILoginPayload {
  email: string
  password: string
}

export interface ILoginResponse {
  accessToken: string
  refreshToken: string
  tokenType: string
  tokenExpires: string
}

export interface IRegisterPayload {
  name: string
  email: string
  password: string
  role: string
}

export interface IRegisterResponse {
  id: string
  name: string
  email: string
  role: string
  flowCount: number
  createdAt: string
  updatedAt: string
}
