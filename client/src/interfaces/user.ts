export enum EUserRole {
  ADMIN = 'ADMIN',
  USER = 'USER',
}

export interface IUser {
  id: string
  name: string
  email: string
  role: EUserRole
  flowCount: number
  firstAccess: boolean
  createdAt: string
  updatedAt: string
}

export interface IUserCredentials {
  email: string
  password: string
}
