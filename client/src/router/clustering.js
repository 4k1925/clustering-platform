import axios from 'axios'

export const getAlgorithmIntro = (algorithm) => {
  return axios.get(`/api/clustering/intro/${algorithm}`)
}

export const runClusterCode = (code) => {
  return axios.post('/api/clustering/run', { code })
}

export const simulateAlgorithm = (algorithm, params) => {
  return axios.post(`/api/clustering/simulate/${algorithm}`, params)
}

export const getVideoList = () => {
  return axios.get('/api/clustering/videos')
}
