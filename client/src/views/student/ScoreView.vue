<template>
  <div class="score-view">
    <el-card>
      <template #header>
        <h2>我的成绩</h2>
      </template>

      <el-table :data="scores" style="width: 100%">
        <el-table-column prop="title" label="报告标题" width="200" />
        <el-table-column prop="score" label="成绩" width="120">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.score)">
              {{ row.score || '待批阅' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="feedback" label="教师反馈" />
        <el-table-column prop="submitted_at" label="提交时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import studentAPI from '@/api/student'

const scores = ref([])

const getScoreType = (score) => {
  if (!score) return 'info'
  if (score >= 85) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

onMounted(async () => {
  try {
    const response = await studentAPI.getScores()
    scores.value = response.data
  } catch (error) {
    console.error('获取成绩失败:', error)
  }
})
</script>

<style scoped>
.score-view {
  padding: 20px;
}
</style>
