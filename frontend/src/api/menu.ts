import request from './request'

export interface MenuItem {
  id: number
  name: string
  path: string
  permission: string
  icon: string
  component: string
  sort: number
  status: 'active' | 'inactive'
  parentId: number | null
  children?: MenuItem[]
}

export function getMenuTreeApi() {
  return request.get('/menus/tree') as Promise<MenuItem[]>
}

export function createMenuApi(data: Omit<MenuItem, 'id' | 'children'>) {
  return request.post('/menus', data) as Promise<MenuItem>
}

export function updateMenuApi(id: number, data: Omit<MenuItem, 'id' | 'children'>) {
  return request.put(`/menus/${id}`, data) as Promise<MenuItem>
}

export function deleteMenuApi(id: number) {
  return request.delete(`/menus/${id}`) as Promise<{ message: string }>
}

export function updateMenuStatusApi(id: number, status: string) {
  return request.patch(`/menus/${id}/status`, { status }) as Promise<{ message: string }>
}
