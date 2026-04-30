import request from './request'

export interface PermissionItem {
  id: number
  name: string
  identifier: string
  type: '菜单' | '按钮' | 'API'
  status: 'active' | 'inactive'
  createdAt: string
}

export function getPermissionListApi(params: { name?: string; type?: string }) {
  return request.get('/permissions/', { params }) as Promise<{ list: PermissionItem[]; total: number }>
}

export function createPermissionApi(data: { name: string; identifier: string; type: string; status: string }) {
  return request.post('/permissions/', data) as Promise<PermissionItem>
}

export function updatePermissionApi(id: number, data: { name: string; identifier: string; type: string; status: string }) {
  return request.put(`/permissions/${id}`, data) as Promise<PermissionItem>
}

export function deletePermissionApi(id: number) {
  return request.delete(`/permissions/${id}`) as Promise<{ message: string }>
}

export function updatePermissionStatusApi(id: number, status: string) {
  return request.patch(`/permissions/${id}/status`, { status }) as Promise<{ message: string }>
}
