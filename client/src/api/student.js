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

getContents(type = null) {
  const params = {}
  if (type) {
    params.type = type
  }
  return axios.get('/student/contents', { params })
    .catch(error => {
      console.error('API调用错误:', error)
      return { data: [] }
    })
},

// 修改getVideos方法
getVideos() {
  return axios.get('/student/videos')
    .catch(error => {
      console.error('获取视频失败:', error)
      // 返回一个带有空数据的响应，避免前端崩溃
      return { data: [] }
    })
},

// 添加获取文章的方法
getArticles() {
  return axios.get('/student/contents', { params: { type: 'article' } })
}
}
