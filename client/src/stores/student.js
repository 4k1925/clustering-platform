import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/utils/axios'

export const useStudentStore = defineStore('student', () => {

  // 状态
  const reports = ref([])
  const scores = ref([])
  const contents = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // 计算属性
  const submittedReports = computed(() =>
    reports.value.filter(r => r.status === 'submitted' || r.status === 'reviewed')
  )

  const draftReports = computed(() =>
    reports.value.filter(r => r.status === 'draft')
  )

  // 动作
  const fetchReports = async () => {
    try {
      isLoading.value = true
      const response = await axios.get('/student/reports')
      reports.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
    } finally {
      isLoading.value = false
    }
  }

  const fetchScores = async () => {
    try {
      isLoading.value = true
      const response = await axios.get('/student/scores')
      scores.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
    } finally {
      isLoading.value = false
    }
  }

  const fetchContents = async () => {
    try {
      isLoading.value = true
      const response = await axios.get('/student/contents')
      contents.value = response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
    } finally {
      isLoading.value = false
    }
  }

  const submitReport = async (reportId) => {
    try {
      isLoading.value = true
      await axios.patch(`/student/reports/${reportId}/submit`)
      await fetchReports()
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createReport = async (reportData) => {
    try {
      isLoading.value = true
      const response = await axios.post('/student/reports', reportData)
      reports.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    reports,
    scores,
    contents,
    isLoading,
    error,
    submittedReports,
    draftReports,
    fetchReports,
    fetchScores,
    fetchContents,
    submitReport,
    createReport
  }
})
