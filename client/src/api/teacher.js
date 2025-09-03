// client/src/api/teacher.js
import axios from '../utils/axios'

// 文件上传基础URL
export const uploadUrl = '/teacher/upload'
export const videoUploadUrl = '/teacher/videos/upload'
export const materialUploadUrl = '/teacher/materials/upload'

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

// 成绩管理
  getScoreStatistics: (classId) => axios.get(`/teacher/scores/statistics?class_id=${classId}`),
  getClassScores: (classId) => axios.get(`/teacher/scores/class/${classId}`),

  // 报告批阅
  getReports: (classId, status) => axios.get(`/teacher/reports?class_id=${classId}&status=${status}`),
  reviewReport: (reportId, data) => axios.post(`/teacher/reports/${reportId}/review`, data),

  downloadReport: (reportId, config = {}) =>
  axios.get(`/teacher/reports/${reportId}/download`, {
    responseType: 'blob',
    ...config
  }),
    getContentsByType(classId, contentType) {
    return axios.get(`/contents?class_id=${classId}&type=${contentType}`)
  },

  // 视频管理API
  getVideos(classId) {
    return axios.get(`/teacher/videos?class_id=${classId}`)
      .then(response => {
        console.log('视频API响应:', response)
        return response.data // 直接返回数据数组
      })
      .catch(error => {
        console.error('获取视频失败:', error)
        throw error
      })
  },

  uploadVideo(formData) {
    return axios.post('/teacher/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 60000, // 视频上传可能需要更长时间
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`视频上传进度: ${percentCompleted}%`)
        // 这里可以添加进度回调函数
      }
    })
  },

  updateVideo(videoId, data) {
    return axios.put(`/teacher/videos/${videoId}`, data)
  },

  deleteVideo(videoId) {
    return axios.delete(`/teacher/videos/${videoId}`)
  },

  // 课程资料管理API
  getMaterials(classId) {
    return axios.get(`/teacher/materials?class_id=${classId}`)
      .then(response => {
        console.log('资料API响应:', response)
        return response.data
      })
      .catch(error => {
        console.error('获取资料失败:', error)
        throw error
      })
  },
  uploadMaterial(formData) {
    return axios.post('/teacher/materials/upload', formData, { // 修改这里
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 30000,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        console.log(`资料上传进度: ${percentCompleted}%`)
      }
    })
  },

  updateMaterial(materialId, data) {
    return axios.put(`/teacher/materials/${materialId}`, data)
  },

  deleteMaterial(materialId) {
    return axios.delete(`/teacher/materials/${materialId}`)
  }
}
