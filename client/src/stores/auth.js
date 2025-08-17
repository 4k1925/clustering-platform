// client/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { login, register, resetPassword, forgotPassword,
  getProfile, updateProfile} from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const user = ref(null)
  const token = ref(null)
  const isAuthenticated = computed(() => !!token.value)
  const isTeacher = computed(() => user.value?.role === 'teacher')
  const isStudent = computed(() => user.value?.role === 'student')

  // 初始化函数改为内部使用
  const initialize = () => {
    const storedToken = localStorage.getItem('authToken')
    if (storedToken) {
      token.value = storedToken
      // 这里可以添加验证token有效性的逻辑
    }
  }
  const fetchUser = async () => {
    try {
      const response = await getProfile()
      user.value = response.data // 假设返回格式为 { data: userInfo }
      return response
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }
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
      setUser(response.user, response.token) // 确保后端返回的是token字段

      if (response.user.role === 'teacher') {
        router.push('/teacher')
      } else {
        router.push('/student/home')
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
      await logout()
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
  // 新增：更新个人信息
  const updateUserProfile = async (profileData) => {
    try {
      const response = await updateProfile(profileData)
      user.value = response.data // 更新store中的用户信息
      return response
    } catch (error) {
      console.error('更新个人信息失败:', error)
      throw error
    }
  }
  // 初始化store
  initialize()

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
    clearUser,
    fetchUser,
    updateUserProfile
  }
})
