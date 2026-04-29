export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  username: string
}

export function loginApi(params: LoginParams): Promise<LoginResult> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (params.username === 'admin' && params.password === 'admin123') {
        resolve({ token: 'mock-token-' + Date.now(), username: params.username })
      } else {
        reject(new Error('用户名或密码错误'))
      }
    }, 500)
  })
}

export interface UserInfo {
  username: string
  avatar: string
}

export function getUserInfoApi(): Promise<UserInfo> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ username: 'admin', avatar: '' })
    }, 200)
  })
}
