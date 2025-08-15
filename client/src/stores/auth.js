import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { login, register, resetPassword, forgotPassword } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const user = ref(null)
  const token = ref(null)
  const isAuthenticated = computed(() => !!token.value)
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  const setUser = (userData, authToken) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem('authToken', authToken)
  }

  const clearUser = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('authToken')
  }

  const loginUser = async (credentials) => {
    try {
      const response = await login(credentials)
      setUser(response.user, response.access_token)

      // 根据角色跳转到不同页面
      if (response.user.role === 'teacher') {
        router.push('/teacher')
      } else {
        router.push('/student')
      }
      return true
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  const registerUser = async (userData) => {
    try {
      const response = await register(userData)
      return response
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  const logout = () => {
    clearUser()
    router.push('/login')
  }

  const changePassword = async (passwordData) => {
    try {
      await resetPassword(passwordData)
      return true
    } catch (error) {
      console.error('修改密码失败:', error)
      throw error
    }
  }

  const requestPasswordReset = async (email) => {
    try {
      await forgotPassword(email)
      return true
    } catch (error) {
      console.error('请求重置密码失败:', error)
      throw error
    }
  }

  // 初始化时检查本地存储的token
  const init = () => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      token.value = storedToken
      // 实际应用中应该验证token有效性
    }
  }

  init()

  return {
    user,
    token,
    isAuthenticated,
    isTeacher,
    isStudent,
    loginUser,
    registerUser,
    logout,
    changePassword,
    requestPasswordReset,
    clearUser
  }
})
