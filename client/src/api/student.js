import axios from '@/utils/axios'

export default {
  // 获取算法介绍内容
  getAlgorithmContent(algorithm) {
    return axios.get(`/student/algorithms/${algorithm}`)
  },

  // 提交代码执行
  executeCode(codeData) {
    return axios.post('/student/code/execute', codeData)
  },

  // 获取实验报告列表
  getReports() {
    return axios.get('/student/reports')
  },

  // 创建实验报告
  createReport(reportData) {
    return axios.post('/student/reports', reportData)
  },

  // 提交实验报告
  submitReport(reportId) {
    return axios.patch(`/student/reports/${reportId}/submit`)
  },

  // 获取成绩信息
  getScores() {
    return axios.get('/student/scores')
  },

  // 获取算法模拟数据
  getSimulationData(algorithm, params) {
    return axios.get(`/student/simulation/${algorithm}`, { params })
  },

  // 获取学生班级列表
  getClasses() {
    return axios.get('/student/classes')
  },

  // 获取视频列表
  getVideos(classId) {
    return axios.get(`/student/videos?class_id=${classId || ''}`)
  },

  // 获取视频详情
  getVideoDetail(videoId) {
    return axios.get(`/student/videos/${videoId}`)
  },

  // 记录视频观看历史
  recordWatchHistory(videoId, progress) {
    return axios.post(`/student/videos/${videoId}/history`, { progress })
  },

  // 获取视频推荐
  getVideoRecommendations(videoId) {
    return axios.get(`/student/videos/${videoId}/recommendations`)
  },

  // 获取课程资料列表
  getMaterials(classId) {
    return axios.get(`/student/materials?class_id=${classId || ''}`)
  },

  // 获取课程资料详情
  getMaterialDetail(materialId) {
    return axios.get(`/student/materials/${materialId}`)
  },

  // 下载课程资料
  downloadMaterial(materialId) {
    return axios.get(`/student/materials/${materialId}/download`, {
      responseType: 'blob'
    })
  }
}
