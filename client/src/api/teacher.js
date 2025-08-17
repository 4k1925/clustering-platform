import axios from '../utils/axios'

export default {
  // 班级管理
  getClasses: () => axios.get('/teacher/classes'),
  createClass: (data) => axios.post('/teacher/classes', data),
  updateClass: (id, data) => axios.put(`/teacher/classes/${id}`, data),
  deleteClass: (id) => axios.delete(`/teacher/classes/${id}`),

  // 学生管理
  getStudents: (classId) => axios.get(`/teacher/students?class_id=${classId}`),
  importStudents: (classId, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post(`/teacher/students/import?class_id=${classId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  resetPassword: (userId) => axios.post(`/teacher/students/${userId}/reset-password`),

  // 内容管理
  getContents: (classId) => axios.get(`/teacher/contents?class_id=${classId}`),
  createContent: (data) => axios.post('/teacher/contents', data),
  updateContent: (id, data) => axios.put(`/teacher/contents/${id}`, data),
  deleteContent: (id) => axios.delete(`/teacher/contents/${id}`),

  // 成绩管理
  getScores: (classId) => axios.get(`/teacher/scores?class_id=${classId}`),
  updateScore: (reportId, data) => axios.put(`/teacher/scores/${reportId}`, data),

  // 报告批阅
  getReports: (classId, status) => axios.get(`/teacher/reports?class_id=${classId}&status=${status}`),
  reviewReport: (reportId, data) => axios.post(`/teacher/reports/${reportId}/review`, data)
}
