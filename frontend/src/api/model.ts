export interface ModelItem {
  id: number
  name: string
  provider: string
  status: 'active' | 'inactive'
  createdAt: string
}

export interface ModelListParams {
  name?: string
  provider?: string
  page?: number
  pageSize?: number
}

export interface ModelListResult {
  list: ModelItem[]
  total: number
}

const mockData: ModelItem[] = [
  { id: 1, name: 'GPT-4o', provider: 'OpenAI', status: 'active', createdAt: '2024-01-10 10:00:00' },
  { id: 2, name: 'Claude Opus 4', provider: 'Anthropic', status: 'active', createdAt: '2024-02-15 14:30:00' },
  { id: 3, name: 'Gemini 2.5', provider: 'Google', status: 'inactive', createdAt: '2024-03-20 09:15:00' },
]

let nextId = 4

export function getModelListApi(params: ModelListParams): Promise<ModelListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.name) {
        list = list.filter((item) => item.name.toLowerCase().includes(params.name!.toLowerCase()))
      }
      if (params.provider) {
        list = list.filter((item) => item.provider === params.provider)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createModelApi(data: Omit<ModelItem, 'id' | 'createdAt'>): Promise<ModelItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: ModelItem = {
        ...data,
        id: nextId++,
        createdAt: new Date().toLocaleString('zh-CN').replace(/\//g, '-'),
      }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updateModelApi(id: number, data: Omit<ModelItem, 'id' | 'createdAt'>): Promise<ModelItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('模型不存在'))
        return
      }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deleteModelApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('模型不存在'))
        return
      }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
