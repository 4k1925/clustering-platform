import request from '../utils/axios'

export const getReports = () => {
  return request.get('/student/reports')
}

export const createReport = (formData) => {
  return request.post('/student/reports', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'  // 确保设置正确的 Content-Type
    }
  })
}

export const updateReport = (id, formData) => {
  return request.put(`/student/reports/${id}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const submitReport = (id) => {
  return request.post(`/student/reports/${id}/submit`)
}

export const deleteReport = (id) => {
  return request.delete(`/student/reports/${id}`)
}

export const getReport = (id) => {
  return request.get(`/student/reports/${id}`)
}
