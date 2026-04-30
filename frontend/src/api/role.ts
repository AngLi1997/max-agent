import request from './request'

export interface RoleItem {
  id: number
  name: string
  code: string
  description: string
  status: 'active' | 'inactive'
  isBuiltin: boolean
  createdAt: string
}

export function getRoleListApi(params: { name?: string; status?: string }) {
  return request.get('/roles/', { params }) as Promise<{ list: RoleItem[]; total: number }>
}

export function createRoleApi(data: { name: string; code: string; description: string; status: string }) {
  return request.post('/roles/', data) as Promise<RoleItem>
}

export function updateRoleApi(id: number, data: { name: string; code: string; description: string; status: string }) {
  return request.put(`/roles/${id}`, data) as Promise<RoleItem>
}

export function deleteRoleApi(id: number) {
  return request.delete(`/roles/${id}`) as Promise<{ message: string }>
}

export function updateRoleStatusApi(id: number, status: string) {
  return request.patch(`/roles/${id}/status`, { status }) as Promise<{ message: string }>
}

export function getRolePermissionsApi(id: number) {
  return request.get(`/roles/${id}/permissions`) as Promise<{ permissionIds: number[] }>
}

export function updateRolePermissionsApi(id: number, permissionIds: number[]) {
  return request.put(`/roles/${id}/permissions`, { permissionIds }) as Promise<{ message: string }>
}
