import axios from '@/utils/axios'

// 简单的请求日志
const originalRequest = axios.request;
axios.request = function(config) {
  console.log('API 请求:', config.method?.toUpperCase(), config.url);
  return originalRequest.call(this, config);
}

export const getAlgorithmIntro = (algorithm) => {
  return axios.get(`/clustering/intro/${algorithm}`)
}

export const runClusterCode = (code) => {
  return axios.post('/clustering/run', { code })
}

export const simulateAlgorithm = (algorithm, params) => {
  console.log('调用 simulateAlgorithm:', algorithm, params);
  return axios.post(`/clustering/simulate/${algorithm}`, params, {
    timeout: 30000
  })
}
// 在 simulateAlgorithm 中添加 GMM 支持

export const getVideoList = () => {
  return axios.get('/clustering/videos')
}

export const getDataTypes = () => {
  return axios.get('/clustering/data-types')
}

export const getCentroidMethods = () => {
  return axios.get('/clustering/centroid-methods')
}