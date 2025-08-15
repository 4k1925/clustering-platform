import axios from 'axios'

export const submitReport = (reportData) => {
  return axios.post('/api/reports', reportData)
}

export const getMyReports = () => {
  return axios.get('/api/reports/me')
}

export const withdrawReport = (id) => {
  return axios.delete(`/api/reports/${id}`)
}

export const gradeReport = (id, gradeData) => {
  return axios.post(`/api/reports/${id}/grade`, gradeData)
}
