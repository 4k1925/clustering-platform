import axios from '@/utils/axios'

export const login = (credentials) => {
  return axios.post('/api/auth/login', credentials)
}

export const logout = () => {
  return axios.post('/api/auth/logout')
}

export const getCurrentUser = () => {
  return axios.get('/api/auth/me')
}

export const resetPassword = (data) => {
  return axios.post('/api/auth/reset-password', data)
}
