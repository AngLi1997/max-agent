export interface PermissionItem {
  id: number
  name: string
  identifier: string
  type: '菜单' | '按钮' | 'API'
  status: 'active' | 'inactive'
  createdAt: string
}

export interface PermissionListParams {
  name?: string
  type?: string
}

export interface PermissionListResult {
  list: PermissionItem[]
  total: number
}

const mockData: PermissionItem[] = [
  { id: 1, name: '用户查看', identifier: 'user:read', type: '菜单', status: 'active', createdAt: '2024-01-01 10:00:00' },
  { id: 2, name: '用户新增', identifier: 'user:create', type: '按钮', status: 'active', createdAt: '2024-02-01 10:00:00' },
  { id: 3, name: '模型查看', identifier: 'model:read', type: 'API', status: 'active', createdAt: '2024-03-01 10:00:00' },
]
let nextId = 4

export function getPermissionListApi(params: PermissionListParams): Promise<PermissionListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.name) {
        list = list.filter((item) => item.name.includes(params.name!))
      }
      if (params.type) {
        list = list.filter((item) => item.type === params.type)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createPermissionApi(data: Omit<PermissionItem, 'id' | 'createdAt'>): Promise<PermissionItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: PermissionItem = {
        ...data,
        id: nextId++,
        createdAt: new Date().toLocaleString('zh-CN').replace(/\//g, '-'),
      }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updatePermissionApi(id: number, data: Omit<PermissionItem, 'id' | 'createdAt'>): Promise<PermissionItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('权限不存在')); return }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deletePermissionApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('权限不存在')); return }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
