import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器添加token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

export const login = (credentials) => {
  return api.post('/auth/login', credentials)
    .then(response => response.data)
}

export const register = (userData) => {
  return api.post('/auth/register', userData)
    .then(response => response.data)
}

export const resetPassword = (passwordData) => {
  return api.post('/auth/reset-password', passwordData)
    .then(response => response.data)
}

export const forgotPassword = (email) => {
  return api.post('/auth/forgot-password', { email })
    .then(response => response.data)
}
// 获取当前用户信息
export const getProfile = () => {
  return api.get('/auth/me')
    .then(response => response.data)
}

// 更新用户信息
export const updateProfile = (profileData) => {
  return api.put('/auth/profile', profileData)
    .then(response => response.data)
}

// 修改密码（区分于重置密码）
export const changePassword = (passwordData) => {
  return api.post('/auth/change-password', passwordData)
    .then(response => response.data)
}

// 头像上传（可选）
export const uploadAvatar = (formData) => {
  return api.post('/auth/upload-avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }).then(response => response.data)
}

export default api
