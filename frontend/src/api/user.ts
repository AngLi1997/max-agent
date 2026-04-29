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

export interface UserListItem {
  id: number
  username: string
  email: string
  roles: RoleSummary[]
  roleIds: number[]
  status: 'active' | 'inactive'
  createdAt: string
  isBuiltin: boolean
}

export interface CreateUserResponse {
  user: UserListItem
  temporaryPassword: string
}

export function getUserListApi(params: { username?: string; status?: string }) {
  return request.get('/users', { params }) as Promise<{ list: UserListItem[]; total: number }>
}

export function createUserApi(data: { username: string; email: string; roleIds: number[]; status: string }) {
  return request.post('/users', data) as Promise<CreateUserResponse>
}

export function updateUserApi(id: number, data: { username: string; email: string; roleIds: number[]; status: string }) {
  return request.put(`/users/${id}`, data) as Promise<UserListItem>
}

export function deleteUserApi(id: number) {
  return request.delete(`/users/${id}`) as Promise<{ message: string }>
}

export function updateUserStatusApi(id: number, status: string) {
  return request.patch(`/users/${id}/status`, { status }) as Promise<{ message: string }>
}
