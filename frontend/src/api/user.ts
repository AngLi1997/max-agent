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

export interface RoleSummary {
  id: number
  name: string
  code: string
}

export interface MenuSummary {
  id: number
  name: string
  path: string
  permission: string
  icon: string
  component: string
  sort: number
  status: 'active' | 'inactive'
  parentId: number | null
  children: MenuSummary[]
}

export interface UserInfo {
  id: number
  username: string
  email: string
  avatar: string
  roles: RoleSummary[]
  permissions: string[]
  menus: MenuSummary[]
  mustChangePassword: boolean
}

export function getUserInfoApi(): Promise<UserInfo> {
  return request.get('/auth/me') as Promise<UserInfo>
}

export function logoutApi(): Promise<{ message: string }> {
  return request.post('/auth/logout') as Promise<{ message: string }>
}

export function changePasswordApi(params: { oldPassword: string; newPassword: string }): Promise<{ message: string }> {
  return request.post('/auth/change-password', params) as Promise<{ message: string }>
}
