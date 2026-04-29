export interface RoleItem {
  id: number
  name: string
  code: string
  description: string
  status: 'active' | 'inactive'
  createdAt: string
}

export interface RoleListParams {
  name?: string
  status?: string
}

export interface RoleListResult {
  list: RoleItem[]
  total: number
}

const mockData: RoleItem[] = [
  { id: 1, name: '超级管理员', code: 'admin', description: '拥有所有权限', status: 'active', createdAt: '2024-01-01 10:00:00' },
  { id: 2, name: '编辑', code: 'editor', description: '可编辑内容', status: 'active', createdAt: '2024-02-01 10:00:00' },
  { id: 3, name: '访客', code: 'viewer', description: '只读权限', status: 'inactive', createdAt: '2024-03-01 10:00:00' },
]
let nextId = 4

export function getRoleListApi(params: RoleListParams): Promise<RoleListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.name) {
        list = list.filter((item) => item.name.includes(params.name!))
      }
      if (params.status) {
        list = list.filter((item) => item.status === params.status)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createRoleApi(data: Omit<RoleItem, 'id' | 'createdAt'>): Promise<RoleItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: RoleItem = {
        ...data,
        id: nextId++,
        createdAt: new Date().toLocaleString('zh-CN').replace(/\//g, '-'),
      }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updateRoleApi(id: number, data: Omit<RoleItem, 'id' | 'createdAt'>): Promise<RoleItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('角色不存在')); return }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deleteRoleApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('角色不存在')); return }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
