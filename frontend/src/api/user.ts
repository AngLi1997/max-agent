import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  username: string
}

export function loginApi(params: LoginParams): Promise<LoginResult> {
  return request.post('/auth/login', params) as Promise<LoginResult>
}

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar: string
  role: string
}

export function getUserInfoApi(): Promise<UserInfo> {
  return request.get('/auth/me') as Promise<UserInfo>
}

export function logoutApi(): Promise<{ message: string }> {
  return request.post('/auth/logout') as Promise<{ message: string }>
}
