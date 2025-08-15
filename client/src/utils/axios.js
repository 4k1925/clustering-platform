import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000', // 后端地址
  withCredentials: true, // 允许携带cookie
  timeout: 10000 // 超时时间
})

// 请求拦截器
api.interceptors.request.use(config => {
  // 可以在这里添加token等
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
api.interceptors.response.use(response => {
  return response.data
}, error => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // 处理未授权
        break
      case 403:
        // 处理禁止访问
        break
      case 404:
        // 处理未找到
        break
      default:
        // 其他错误
    }
  }
  return Promise.reject(error)
})

export default api
