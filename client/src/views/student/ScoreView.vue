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

.score-view ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.score-view ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
}

.score-view ::v-deep(.el-card__header h2) {
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 24px;
  font-weight: 600;
}

.score-view ::v-deep(.el-table) {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

.score-view ::v-deep(.el-table th) {
  background: rgba(255, 255, 255, 0.1);
  color: #333;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.score-view ::v-deep(.el-table td) {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.score-view ::v-deep(.el-table tr:hover td) {
  background: rgba(102, 126, 234, 0.1);
}

.score-view ::v-deep(.el-tag) {
  border: none;
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

.score-view ::v-deep(.el-tag.el-tag--success) {
  background: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.score-view ::v-deep(.el-tag.el-tag--warning) {
  background: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}

.score-view ::v-deep(.el-tag.el-tag--danger) {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}

.score-view ::v-deep(.el-tag.el-tag--info) {
  background: rgba(144, 147, 153, 0.2);
  color: #909399;
}
</style>
