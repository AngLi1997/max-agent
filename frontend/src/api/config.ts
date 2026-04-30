import request from './request'

export interface ConfigItem {
  id: number
  name: string
  key: string
  value: string
  description: string
}

export function getConfigListApi(params: { key?: string }) {
  return request.get('/configs/', { params }) as Promise<{ list: ConfigItem[]; total: number }>
}

export function createConfigApi(data: Omit<ConfigItem, 'id'>) {
  return request.post('/configs/', data) as Promise<ConfigItem>
}

export function updateConfigApi(id: number, data: Omit<ConfigItem, 'id'>) {
  return request.put(`/configs/${id}`, data) as Promise<ConfigItem>
}

export function deleteConfigApi(id: number) {
  return request.delete(`/configs/${id}`) as Promise<{ message: string }>
}
