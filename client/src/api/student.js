import axios from '@/utils/axios'

export default {
  // 获取算法介绍内容
  getAlgorithmContent(algorithm) {
    return axios.get(`/student/algorithms/${algorithm}`)
  },

  // 获取教学视频列表
  getVideos() {
    return axios.get('/student/videos')
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
  }
}
