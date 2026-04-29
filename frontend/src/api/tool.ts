export interface ToolItem {
  id: number
  name: string
  type: '搜索' | '执行' | '文件'
  status: 'active' | 'inactive'
  createdAt: string
}

export interface ToolListParams {
  name?: string
  type?: '搜索' | '执行' | '文件'
  page?: number
  pageSize?: number
}

export interface ToolListResult {
  list: ToolItem[]
  total: number
}

const mockData: ToolItem[] = [
  { id: 1, name: 'Web Search', type: '搜索', status: 'active', createdAt: '2024-01-08 10:00:00' },
  { id: 2, name: 'Code Executor', type: '执行', status: 'active', createdAt: '2024-02-12 14:30:00' },
  { id: 3, name: 'File Reader', type: '文件', status: 'inactive', createdAt: '2024-03-18 09:15:00' },
]

let nextId = 4

export function getToolListApi(params: ToolListParams): Promise<ToolListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.name) {
        list = list.filter((item) => item.name.toLowerCase().includes(params.name!.toLowerCase()))
      }
      if (params.type) {
        list = list.filter((item) => item.type === params.type)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createToolApi(data: Omit<ToolItem, 'id' | 'createdAt'>): Promise<ToolItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: ToolItem = {
        ...data,
        id: nextId++,
        createdAt: new Date().toLocaleString('zh-CN').replace(/\//g, '-'),
      }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updateToolApi(id: number, data: Omit<ToolItem, 'id' | 'createdAt'>): Promise<ToolItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('工具不存在'))
        return
      }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deleteToolApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('工具不存在'))
        return
      }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
