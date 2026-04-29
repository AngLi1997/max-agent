export interface ConfigItem {
  id: number
  name: string
  key: string
  value: string
  description: string
}

export interface ConfigListParams {
  key?: string
}

export interface ConfigListResult {
  list: ConfigItem[]
  total: number
}

const mockData: ConfigItem[] = [
  { id: 1, name: '站点名称', key: 'site.name', value: 'Max-Agent', description: '系统站点名称' },
  { id: 2, name: '站点描述', key: 'site.description', value: 'AI Agent管理平台', description: '系统站点描述' },
  { id: 3, name: '上传限制', key: 'upload.maxSize', value: '10MB', description: '单文件上传大小限制' },
]
let nextId = 4

export function getConfigListApi(params: ConfigListParams): Promise<ConfigListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.key) {
        list = list.filter((item) => item.key.includes(params.key!))
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createConfigApi(data: Omit<ConfigItem, 'id'>): Promise<ConfigItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: ConfigItem = { ...data, id: nextId++ }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updateConfigApi(id: number, data: Omit<ConfigItem, 'id'>): Promise<ConfigItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('配置项不存在')); return }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deleteConfigApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) { reject(new Error('配置项不存在')); return }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
