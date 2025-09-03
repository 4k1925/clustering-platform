// stores/teacher.js
import { defineStore } from 'pinia'
import teacherApi from '../api/teacher'

export const useTeacherStore = defineStore('teacher', {
  state: () => ({
    classes: [],
    currentClass: null,
    students: [],
    contents: [],
    reports: [],
    scores: [],
    classesList: [],
    scoreStatistics: null,
    classScores: []

  }),

  actions: {
    // 班级管理
    async fetchClasses() {
      try {
        const res = await teacherApi.getClasses()
        this.classes = res || []
        return this.classes
      } catch (error) {
        console.error('获取班级列表失败:', error)
        this.classes = []  // 出错时重置为空数组
        throw error
      }
    },

    async createClass(data) {
      try {
        const res = await teacherApi.createClass(data)
        const newClass = res

        if (newClass) {
          this.classes = [...this.classes, newClass]
        }
        return newClass
      } catch (error) {
        console.error('创建班级失败:', error)
        throw error
      }
    },

    async updateClass(id, data) {
      try {
        const res = await teacherApi.updateClass(id, data)
        const updatedClass = res

        if (updatedClass) {
          this.classes = this.classes.map(cls =>
            cls.class_id === id ? updatedClass : cls
          )
        }
        return updatedClass
      } catch (error) {
        console.error('更新班级失败:', error)
        throw error
      }
    },

    async deleteClass(id) {
      try {
        await teacherApi.deleteClass(id)
        // 确保 this.classes 是数组
        this.classes = this.classes.filter(cls => cls.class_id !== id)
      } catch (error) {
        console.error('删除班级失败:', error)
        throw error
      }
    },

// 学生管理
    async fetchStudents(classId) {
      try {
        const students = await teacherApi.getStudents(classId)
        console.log('获取学生列表数据:', students) // 添加调试信息
        this.students = Array.isArray(students) ? students : []
        this.currentClass = classId
        return this.students
      } catch (error) {
        console.error('获取学生列表失败:', error)
        this.students = [] // 出错时重置为空数组
        throw error
      }
    },

// 导入学生
    async importStudents(classId, file) {
      try {
        const result = await teacherApi.importStudents(classId, file)
        console.log('导入学生结果:', result) // 添加调试信息

        // 导入成功后重新获取学生列表
        await this.fetchStudents(classId)

        return result
      } catch (error) {
        console.error('导入学生失败:', error)
        throw error
      }
    },

    // 内容管理
async fetchContents(classId) {
  try {
    const response = await teacherApi.getContents(classId)
    console.log('获取内容列表响应:', response)

    // 处理不同的响应格式
    if (Array.isArray(response)) {
      this.contents = response
    } else if (response && Array.isArray(response.data)) {
      this.contents = response.data
    } else {
      console.error('获取内容列表: 响应格式不正确', response)
      this.contents = []
    }
    return this.contents
  } catch (error) {
    console.error('获取内容列表失败:', error)
    this.contents = []
    throw error
  }
},

async createContent(data) {
  try {
    const response = await teacherApi.createContent(data)
    console.log('创建内容响应:', response)

    // 处理响应格式
    const newContent = response.data || response

    // 创建成功后重新获取内容列表，确保数据最新
    if (data.class_id) {
      await this.fetchContents(data.class_id)
    }

    return newContent
  } catch (error) {
    console.error('创建内容失败:', error)
    throw error
  }
},

async updateContent(id, data) {
  try {
    const response = await teacherApi.updateContent(id, data)
    console.log('更新内容响应:', response)

    // 处理响应格式
    const updatedContent = response.data || response

    if (updatedContent) {
      const index = this.contents.findIndex(c => c.content_id === id)
      if (index !== -1) {
        this.contents[index] = updatedContent
      }
    }
    return updatedContent
  } catch (error) {
    console.error('更新内容失败:', error)
    throw error
  }
},

async deleteContent(id) {
  try {
    await teacherApi.deleteContent(id)
    this.contents = this.contents.filter(c => c.content_id !== id)
  } catch (error) {
    console.error('删除内容失败:', error)
    throw error
  }
},


async fetchReports(classId, status = 'submitted') {
  try {
    const res = await teacherApi.getReports(classId, status)
    console.log('获取报告响应:', res) // 添加调试日志

    // 修改这里：直接使用 res 而不是 res.data
    this.reports = res || []
    return this.reports
  } catch (error) {
    console.error('获取报告失败:', error)
    this.reports = []
    throw error
  }
},

async reviewReport(reportId, data) {
  try {
    const res = await teacherApi.reviewReport(reportId, data)
    console.log('批阅报告响应:', res)

    // 修改这里：直接使用 res 而不是 res.data
    const reviewedReport = res

    const index = this.reports.findIndex(r => r.report_id === reportId)
    if (index !== -1) {
      this.reports[index] = reviewedReport
    }
    return reviewedReport
  } catch (error) {
    console.error('批阅报告失败:', error)
    throw error
  }
},

 async fetchScoreStatistics(classId) {
    try {
      const res = await teacherApi.getScoreStatistics(classId)
      this.scoreStatistics = res
      return this.scoreStatistics
    } catch (error) {
      console.error('获取成绩统计失败:', error)
      this.scoreStatistics = null
      throw error
    }
  },

  async fetchClassScores(classId) {
    try {
      const res = await teacherApi.getClassScores(classId)
      this.classScores = res
      return this.classScores
    } catch (error) {
      console.error('获取班级成绩失败:', error)
      this.classScores = []
      throw error
    }
  },
  // 内容管理
async fetchMaterials(classId) {
  try {
    const response = await teacherApi.getMaterials(classId)
    this.materials = response.data || response
    return this.materials
  } catch (error) {
    console.error('获取课程资料失败:', error)
    this.materials = []
    throw error
  }
},

async uploadMaterial(formData) {
  try {
    const response = await teacherApi.uploadMaterial(formData)
    return response
  } catch (error) {
    console.error('上传资料失败:', error)
    throw error
  }
},

async updateMaterial(materialId, data) {
  try {
    const response = await teacherApi.updateMaterial(materialId, data)
    return response
  } catch (error) {
    console.error('更新资料失败:', error)
    throw error
  }
},

async deleteMaterial(materialId) {
  try {
    await teacherApi.deleteMaterial(materialId)
    this.materials = this.materials.filter(m => m.id !== materialId)
  } catch (error) {
    console.error('删除资料失败:', error)
    throw error
  }
},

// 视频管理
async fetchVideos(classId) {
  try {
    const response = await teacherApi.getVideos(classId)
    this.videos = response.data || response
    return this.videos
  } catch (error) {
    console.error('获取视频列表失败:', error)
    this.videos = []
    throw error
  }
},

async uploadVideo(formData) {
  try {
    const response = await teacherApi.uploadVideo(formData)
    return response
  } catch (error) {
    console.error('上传视频失败:', error)
    throw error
  }
},

async updateVideo(videoId, data) {
  try {
    const response = await teacherApi.updateVideo(videoId, data)
    return response
  } catch (error) {
    console.error('更新视频失败:', error)
    throw error
  }
},

async deleteVideo(videoId) {
  try {
    await teacherApi.deleteVideo(videoId)
    this.videos = this.videos.filter(v => v.id !== videoId)
  } catch (error) {
    console.error('删除视频失败:', error)
    throw error
  }
}
  }
})
