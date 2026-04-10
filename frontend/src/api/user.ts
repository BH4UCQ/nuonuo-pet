import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  user: {
    id: number
    username: string
    email: string
  }
}

export const userApi = {
  login: (params: LoginParams) =>
    request.post<any, { data: LoginResult }>('/auth/login', params),

  logout: () => request.post('/auth/logout'),

  getCurrentUser: () => request.get<any, { data: any }>('/users/me'),

  updateProfile: (data: any) => request.put('/users/me', data),
}
