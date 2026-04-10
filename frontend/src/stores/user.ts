import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<any>(null)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = null
    localStorage.removeItem('token')
  }

  const fetchUserInfo = async () => {
    if (!token.value) return
    try {
      const res = await userApi.getCurrentUser()
      userInfo.value = res.data
    } catch (error) {
      clearToken()
    }
  }

  const logout = async () => {
    try {
      await userApi.logout()
    } finally {
      clearToken()
      userInfo.value = null
    }
  }

  return {
    token,
    userInfo,
    setToken,
    clearToken,
    fetchUserInfo,
    logout,
  }
})
