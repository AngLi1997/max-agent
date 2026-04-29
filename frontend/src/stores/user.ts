import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<{ username: string; avatar: string } | null>(null)

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('token', t)
  }

  function clearToken() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  function setUserInfo(info: { username: string; avatar: string }) {
    userInfo.value = info
  }

  return { token, userInfo, setToken, clearToken, setUserInfo }
})
