import { defineStore } from 'pinia'
import teacherApi from '../api/teacher'

export const useTeacherStore = defineStore('teacher', {
  state: () => ({
    classes: [],
    currentClass: null,
    students: [],
    contents: [],
    reports: [],
    scores: []
  }),
  actions: {
    // 班级管理
    async fetchClasses() {
      const res = await teacherApi.getClasses()
      this.classes = res.data
      return res.data
    },
    async createClass(data) {
      const res = await teacherApi.createClass(data)
      this.classes.push(res.data)
      return res.data
    },
    async updateClass(id, data) {
      const res = await teacherApi.updateClass(id, data)
      const index = this.classes.findIndex(c => c.class_id === id)
      if (index !== -1) {
        this.classes[index] = res.data
      }
      return res.data
    },
    async deleteClass(id) {
      await teacherApi.deleteClass(id)
      this.classes = this.classes.filter(c => c.class_id !== id)
    },

    // 学生管理
    async fetchStudents(classId) {
      const res = await teacherApi.getStudents(classId)
      this.students = res.data
      return res.data
    },
    async importStudents(classId, file) {
      const res = await teacherApi.importStudents(classId, file)
      this.students = res.data
      return res.data
    },
    async resetPassword(userId) {
      await teacherApi.resetPassword(userId)
    },

    // 内容管理
    async fetchContents(classId) {
      const res = await teacherApi.getContents(classId)
      this.contents = res.data
      return res.data
    },
    async createContent(data) {
      const res = await teacherApi.createContent(data)
      this.contents.push(res.data)
      return res.data
    },
    async updateContent(id, data) {
      const res = await teacherApi.updateContent(id, data)
      const index = this.contents.findIndex(c => c.content_id === id)
      if (index !== -1) {
        this.contents[index] = res.data
      }
      return res.data
    },
    async deleteContent(id) {
      await teacherApi.deleteContent(id)
      this.contents = this.contents.filter(c => c.content_id !== id)
    },

    // 成绩管理
    async fetchScores(classId) {
      const res = await teacherApi.getScores(classId)
      this.scores = res.data
      return res.data
    },
    async updateScore(reportId, data) {
      const res = await teacherApi.updateScore(reportId, data)
      const index = this.scores.findIndex(s => s.report_id === reportId)
      if (index !== -1) {
        this.scores[index] = res.data
      }
      return res.data
    },

    // 报告批阅
    async fetchReports(classId, status = 'submitted') {
      const res = await teacherApi.getReports(classId, status)
      this.reports = res.data
      return res.data
    },
    async reviewReport(reportId, data) {
      const res = await teacherApi.reviewReport(reportId, data)
      const index = this.reports.findIndex(r => r.report_id === reportId)
      if (index !== -1) {
        this.reports[index] = res.data
      }
      return res.data
    }
  }
})
