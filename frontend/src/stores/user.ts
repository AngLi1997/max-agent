import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MenuSummary, RoleSummary, UserInfo } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const roles = ref<RoleSummary[]>([])
  const permissions = ref<string[]>([])
  const menus = ref<MenuSummary[]>([])
  const mustChangePassword = ref(false)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function setAuthPayload(info: UserInfo) {
    userInfo.value = info
    roles.value = info.roles
    permissions.value = info.permissions
    menus.value = info.menus
    mustChangePassword.value = info.mustChangePassword
  }

  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }

  function clearToken() {
    token.value = ''
    userInfo.value = null
    roles.value = []
    permissions.value = []
    menus.value = []
    mustChangePassword.value = false
    localStorage.removeItem('token')
  }

  return { token, userInfo, roles, permissions, menus, mustChangePassword, setToken, setAuthPayload, hasPermission, clearToken }
})
