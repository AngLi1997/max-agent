import request from './request'

export interface OperationLogItem {
  id: number
  operator: string
  module: string
  action: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  result: string
  time: string
  detail: string
}

export interface LoginLogItem {
  id: number
  username: string
  ip: string
  location: string
  device: string
  result: string
  time: string
  detail: string
}

export function getOperationLogApi(params: { operator?: string; module?: string; startTime?: string; endTime?: string }) {
  return request.get('/operation-logs', { params }) as Promise<{ list: OperationLogItem[]; total: number }>
}

export function getLoginLogApi(params: { username?: string; result?: string; startTime?: string; endTime?: string }) {
  return request.get('/login-logs', { params }) as Promise<{ list: LoginLogItem[]; total: number }>
}
