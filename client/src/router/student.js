import axios from 'axios'

export const getStudents = (params = {}) => {
  return axios.get('/api/students', { params })
}

export const createStudent = (studentData) => {
  return axios.post('/api/students', studentData)
}

export const updateStudent = (id, studentData) => {
  return axios.put(`/api/students/${id}`, studentData)
}

export const deleteStudent = (id) => {
  return axios.delete(`/api/students/${id}`)
}

export const importStudents = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return axios.post('/api/students/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
