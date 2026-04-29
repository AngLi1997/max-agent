export interface OperationLogItem {
  id: number
  operator: string
  module: string
  action: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  result: '成功' | '失败'
  time: string
  detail: string
}

export interface LoginLogItem {
  id: number
  username: string
  ip: string
  location: string
  device: string
  result: '成功' | '失败'
  time: string
}

export interface OperationLogParams {
  operator?: string
  module?: string
  startTime?: string
  endTime?: string
}

export interface LoginLogParams {
  username?: string
  result?: string
  startTime?: string
  endTime?: string
}

const operationLogMockData: OperationLogItem[] = [
  { id: 1, operator: 'admin', module: '用户管理', action: '查询用户列表', method: 'GET', result: '成功', time: '2024-04-01 09:00:00', detail: '分页查询用户列表，页码:1，大小:10' },
  { id: 2, operator: 'editor', module: '模型管理', action: '新增模型', method: 'POST', result: '成功', time: '2024-04-01 10:15:00', detail: '新增模型 Claude Opus 4，提供商 Anthropic' },
  { id: 3, operator: 'admin', module: '角色管理', action: '修改角色', method: 'PUT', result: '失败', time: '2024-04-01 11:20:00', detail: '修改角色 editor 失败，参数校验异常' },
  { id: 4, operator: 'viewer', module: '工具管理', action: '删除工具', method: 'DELETE', result: '失败', time: '2024-04-01 14:30:00', detail: '删除工具失败，权限不足' },
  { id: 5, operator: 'admin', module: '系统配置', action: '更新配置', method: 'PUT', result: '成功', time: '2024-04-01 16:45:00', detail: '更新 upload.maxSize 为 20MB' },
]

const loginLogMockData: LoginLogItem[] = [
  { id: 1, username: 'admin', ip: '192.168.1.10', location: '北京', device: 'Chrome 123 / macOS', result: '成功', time: '2024-04-01 08:30:00' },
  { id: 2, username: 'editor', ip: '192.168.1.23', location: '上海', device: 'Edge 122 / Windows 11', result: '成功', time: '2024-04-01 09:12:00' },
  { id: 3, username: 'viewer', ip: '10.0.0.45', location: '广州', device: 'Safari 17 / iOS', result: '失败', time: '2024-04-01 10:05:00' },
  { id: 4, username: 'admin', ip: '172.16.0.8', location: '深圳', device: 'Firefox 124 / Ubuntu', result: '成功', time: '2024-04-01 13:40:00' },
  { id: 5, username: 'guest', ip: '203.0.113.77', location: '杭州', device: 'Chrome 123 / Android', result: '失败', time: '2024-04-01 18:22:00' },
]

export function getOperationLogApi(params: OperationLogParams): Promise<{ list: OperationLogItem[]; total: number }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...operationLogMockData]
      if (params.operator) {
        list = list.filter((item) => item.operator.includes(params.operator!))
      }
      if (params.module) {
        list = list.filter((item) => item.module === params.module)
      }
      if (params.startTime && params.endTime) {
        list = list.filter((item) => item.time >= params.startTime! && item.time <= params.endTime!)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}

export function getLoginLogApi(params: LoginLogParams): Promise<{ list: LoginLogItem[]; total: number }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      let list = [...loginLogMockData]
      if (params.username) {
        list = list.filter((item) => item.username.includes(params.username!))
      }
      if (params.result) {
        list = list.filter((item) => item.result === params.result)
      }
      if (params.startTime && params.endTime) {
        list = list.filter((item) => item.time >= params.startTime! && item.time <= params.endTime!)
      }
      resolve({ list, total: list.length })
    }, 300)
  })
}
