export interface SkillItem {
  id: number
  name: string
  description: string
  status: 'active' | 'inactive'
  createdAt: string
}

export interface SkillListParams {
  name?: string
  status?: 'active' | 'inactive'
  page?: number
  pageSize?: number
}

export interface SkillListResult {
  list: SkillItem[]
  total: number
}

const mockData: SkillItem[] = [
  { id: 1, name: '代码生成', description: '根据自然语言描述自动生成高质量代码，支持多种编程语言', status: 'active', createdAt: '2024-01-12 10:00:00' },
  { id: 2, name: '文档摘要', description: '对长篇文档进行智能摘要，提取关键信息并生成结构化摘要', status: 'active', createdAt: '2024-02-18 14:30:00' },
  { id: 3, name: '数据分析', description: '对结构化数据进行统计分析、趋势预测和可视化建议', status: 'inactive', createdAt: '2024-03-25 09:15:00' },
]

let nextId = 4

function formatDateTime(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

export function getSkillListApi(params: SkillListParams): Promise<SkillListResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...mockData]
      if (params.name) {
        list = list.filter((item) => item.name.toLowerCase().includes(params.name!.toLowerCase()))
      }
      if (params.status) {
        list = list.filter((item) => item.status === params.status)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function createSkillApi(data: Omit<SkillItem, 'id' | 'createdAt'>): Promise<SkillItem> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const item: SkillItem = {
        ...data,
        id: nextId++,
        createdAt: formatDateTime(new Date()),
      }
      mockData.push(item)
      resolve(item)
    }, 300)
  })
}

export function updateSkillApi(id: number, data: Omit<SkillItem, 'id' | 'createdAt'>): Promise<SkillItem> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('技能不存在'))
        return
      }
      mockData[index] = { ...mockData[index], ...data }
      resolve(mockData[index])
    }, 300)
  })
}

export function deleteSkillApi(id: number): Promise<void> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const index = mockData.findIndex((item) => item.id === id)
      if (index === -1) {
        reject(new Error('技能不存在'))
        return
      }
      mockData.splice(index, 1)
      resolve()
    }, 300)
  })
}
