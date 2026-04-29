export interface DashboardStats {
  userCount: number
  modelCount: number
  skillCount: number
  toolCount: number
}

export function getStatsApi(): Promise<DashboardStats> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ userCount: 128, modelCount: 15, skillCount: 42, toolCount: 23 })
    }, 300)
  })
}

export interface TrendItem {
  date: string
  value: number
}

export function getTrendApi(): Promise<TrendItem[]> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { date: '04-23', value: 120 },
        { date: '04-24', value: 132 },
        { date: '04-25', value: 101 },
        { date: '04-26', value: 134 },
        { date: '04-27', value: 90 },
        { date: '04-28', value: 230 },
        { date: '04-29', value: 210 },
      ])
    }, 300)
  })
}
