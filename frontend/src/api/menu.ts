export interface MenuItem {
  id: number
  name: string
  path: string
  permission: string
  sort: number
  status: 'active' | 'inactive'
  parentId: number | null
  children?: MenuItem[]
}

const mockTreeData: MenuItem[] = [
  { id: 1, name: '仪表盘', path: '/dashboard', permission: 'dashboard:view', sort: 1, status: 'active', parentId: null },
  { id: 2, name: '模型管理', path: '/model', permission: 'model:view', sort: 2, status: 'active', parentId: null },
  { id: 3, name: 'Skills管理', path: '/skill', permission: 'skill:view', sort: 3, status: 'active', parentId: null },
  { id: 4, name: '工具管理', path: '/tool', permission: 'tool:view', sort: 4, status: 'active', parentId: null },
  {
    id: 5,
    name: '系统设置',
    path: '/setting',
    permission: 'setting:view',
    sort: 5,
    status: 'active',
    parentId: null,
    children: [
      { id: 51, name: '用户管理', path: '/setting/user', permission: 'setting:user', sort: 1, status: 'active', parentId: 5 },
      { id: 52, name: '角色管理', path: '/setting/role', permission: 'setting:role', sort: 2, status: 'active', parentId: 5 },
      { id: 53, name: '权限管理', path: '/setting/permission', permission: 'setting:permission', sort: 3, status: 'active', parentId: 5 },
      { id: 54, name: '菜单配置', path: '/setting/menu', permission: 'setting:menu', sort: 4, status: 'active', parentId: 5 },
      { id: 55, name: '系统配置', path: '/setting/config', permission: 'setting:config', sort: 5, status: 'active', parentId: 5 },
      { id: 56, name: '操作日志', path: '/setting/operation-log', permission: 'setting:operation-log', sort: 6, status: 'active', parentId: 5 },
      { id: 57, name: '登录日志', path: '/setting/login-log', permission: 'setting:login-log', sort: 7, status: 'active', parentId: 5 },
    ],
  },
]

let nextId = 100

function findAndUpdate(nodes: MenuItem[], id: number, updater: (item: MenuItem) => void): boolean {
  for (const item of nodes) {
    if (item.id === id) {
      updater(item)
      return true
    }
    if (item.children && findAndUpdate(item.children, id, updater)) return true
  }
  return false
}

function findAndDelete(nodes: MenuItem[], id: number): boolean {
  const index = nodes.findIndex((item) => item.id === id)
  if (index !== -1) {
    nodes.splice(index, 1)
    return true
  }
  for (const item of nodes) {
    if (item.children && findAndDelete(item.children, id)) return true
  }
  return false
}

function findById(nodes: MenuItem[], id: number): MenuItem | null {
  for (const item of nodes) {
    if (item.id === id) return item
    if (item.children) {
      const found = findById(item.children, id)
      if (found) return found
    }
  }
  return null
}

export function getMenuTreeApi(): Promise<MenuItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(JSON.parse(JSON.stringify(mockTreeData))), 300)
  })
}

export function createMenuApi(data: Omit<MenuItem, 'id' | 'children'>): Promise<MenuItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newItem: MenuItem = { ...data, id: nextId++ }
      if (newItem.parentId === null) {
        mockTreeData.push(newItem)
      } else {
        const parent = findById(mockTreeData, newItem.parentId)
        if (parent) {
          if (!parent.children) parent.children = []
          parent.children.push(newItem)
        }
      }
      resolve(newItem)
    }, 300)
  })
}

export function updateMenuApi(id: number, data: Omit<MenuItem, 'id' | 'children'>): Promise<MenuItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      let updated: MenuItem | null = null
      const ok = findAndUpdate(mockTreeData, id, (item) => {
        item.name = data.name
        item.path = data.path
        item.permission = data.permission
        item.sort = data.sort
        item.status = data.status
        updated = item
      })
      if (!ok || !updated) {
        reject(new Error('菜单不存在'))
        return
      }
      resolve(updated)
    }, 300)
  })
}

export function deleteMenuApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const ok = findAndDelete(mockTreeData, id)
      if (!ok) {
        reject(new Error('菜单不存在'))
        return
      }
      resolve()
    }, 300)
  })
}
