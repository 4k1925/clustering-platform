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

export default api
