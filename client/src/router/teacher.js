import axios from 'axios'

export const getClasses = () => {
  return axios.get('/api/teacher/classes')
}

export const createClass = (classData) => {
  return axios.post('/api/teacher/classes', classData)
}

export const updateClassContent = (id, content) => {
  return axios.put(`/api/teacher/contents/${id}`, { content })
}

export const getUnreviewedReports = () => {
  return axios.get('/api/teacher/reports/unreviewed')
}
