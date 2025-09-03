// client/src/api/teacher.js
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
    console.log('构建FormData，文件:', file)

    const formData = new FormData()
    formData.append('file', file)
    console.log('文件已添加到FormData')

    // 调试 FormData 内容
    for (let [key, value] of formData.entries()) {
      console.log(`FormData[${key}]:`, value, value instanceof File ? '(File)' : '(其他)')
    }


    return axios.post(`/teacher/students/import?class_id=${classId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`上传进度: ${percentCompleted}%`)
      }
    })
  },
  resetPassword: (userId) => axios.post(`/teacher/students/${userId}/reset-password`),

    getContents(classId) {
    return axios.get(`/teacher/contents?class_id=${classId}`)
  },

  // 创建内容
  createContent(data) {
    return axios.post('/teacher/contents', data)
  },

  // 更新内容
  updateContent(contentId, data) {
    return axios.put(`/teacher/contents/${contentId}`, data)
  },

  // 删除内容
  deleteContent(contentId) {
    return axios.delete(`/teacher/contents/${contentId}`)
  },

  // 上传文件
  uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)
    return axios.post('/teacher/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
// 成绩管理
  getScoreStatistics: (classId) => axios.get(`/teacher/scores/statistics?class_id=${classId}`),
  getClassScores: (classId) => axios.get(`/teacher/scores/class/${classId}`),

  // 报告批阅
  getReports: (classId, status) => axios.get(`/teacher/reports?class_id=${classId}&status=${status}`),
  reviewReport: (reportId, data) => axios.post(`/teacher/reports/${reportId}/review`, data),
  // client/src/api/teacher.js
  downloadReport: (reportId, config = {}) =>
  axios.get(`/teacher/reports/${reportId}/download`, {
    responseType: 'blob',
    ...config
  }),
    getContentsByType(classId, contentType) {
    return axios.get(`/contents?class_id=${classId}&type=${contentType}`)
  }
}
