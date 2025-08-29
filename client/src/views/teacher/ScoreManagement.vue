<template>
  <div class="score-management">
    <div class="header">
      <h2>成绩管理</h2>
      <el-select
        v-model="selectedClass"
        placeholder="选择班级"
        @change="handleClassChange"
        style="width: 300px; margin-left: 20px;"
      >
        <el-option
          v-for="cls in classes"
          :key="cls.class_id"
          :label="`${cls.name} (${cls.course_code})`"
          :value="cls.class_id"
        />
      </el-select>
    </div>

    <div v-if="selectedClass" class="content">
      <!-- 统计信息 -->
      <div class="statistics-section">
        <h3>班级成绩统计</h3>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="chart-container">
              <h4>分数段分布</h4>
              <div v-if="scoreStatistics" style="height: 300px;">
                <PieChart :data="scoreDistributionData" />
              </div>
              <el-empty v-else description="暂无数据" />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="stats-cards">
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">平均分</div>
                  <div class="stat-value">{{ scoreStatistics?.statistics?.average_score || 0 }}</div>
                </div>
              </el-card>
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">最高分</div>
                  <div class="stat-value">{{ scoreStatistics?.statistics?.max_score || 0 }}</div>
                </div>
              </el-card>
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">最低分</div>
                  <div class="stat-value">{{ scoreStatistics?.statistics?.min_score || 0 }}</div>
                </div>
              </el-card>
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">及格率</div>
                  <div class="stat-value">{{ scoreStatistics?.statistics?.pass_rate || 0 }}%</div>
                </div>
              </el-card>
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">总人数</div>
                  <div class="stat-value">{{ scoreStatistics?.total_students || 0 }}</div>
                </div>
              </el-card>
              <el-card class="stat-card">
                <div class="stat-item">
                  <div class="stat-label">已提交</div>
                  <div class="stat-value">{{ scoreStatistics?.submitted_reports || 0 }}</div>
                </div>
              </el-card>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 学生成绩列表 -->
      <div class="scores-list">
        <h3>学生成绩列表</h3>
        <el-table :data="classScores" style="width: 100%" v-loading="loading">
          <el-table-column prop="student_number" label="学号" width="120" />
          <el-table-column prop="student_name" label="姓名" width="100" />
          <el-table-column label="成绩" width="100">
            <template #default="{ row }">
              <el-tag
                :type="getScoreTagType(row.score)"
                v-if="row.score !== null && row.score !== undefined"
              >
                {{ row.score }}
              </el-tag>
              <span v-else>未评分</span>
            </template>
          </el-table-column>
          <el-table-column prop="report_title" label="报告标题" show-overflow-tooltip />
          <el-table-column prop="submitted_at" label="提交时间" width="180">
            <template #default="{ row }">
              {{ row.submitted_at ? formatDate(row.submitted_at) : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)">
                {{ getStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button
                v-if="row.report_title"
                type="primary"
                size="small"
                @click="viewReportDetails(row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <div v-else class="empty-state">
      <el-empty description="请选择班级查看成绩" />
    </div>

    <!-- 报告详情对话框 -->
    <el-dialog
      v-model="reportDialogVisible"
      title="报告详情"
      width="60%"
    >
      <div v-if="selectedReport">
        <h4>{{ selectedReport.report_title }}</h4>
        <p><strong>学生:</strong> {{ selectedReport.student_name }} ({{ selectedReport.student_number }})</p>
        <p><strong>成绩:</strong> {{ selectedReport.score }}</p>
        <p><strong>反馈:</strong></p>
        <el-input
          type="textarea"
          :rows="4"
          :model-value="selectedReport.feedback"
          readonly
        />
        <p><strong>提交时间:</strong> {{ formatDate(selectedReport.submitted_at) }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage } from 'element-plus'
import PieChart from '@/components/charts/PieChart.vue'

const teacherStore = useTeacherStore()
const selectedClass = ref('')
const classes = ref([])
const loading = ref(false)
const reportDialogVisible = ref(false)
const selectedReport = ref(null)

// 计算属性
const scoreStatistics = computed(() => teacherStore.scoreStatistics)
const classScores = computed(() => teacherStore.classScores)

const scoreDistributionData = computed(() => {
  if (!scoreStatistics.value?.statistics?.score_distribution) return []

  const distribution = scoreStatistics.value.statistics.score_distribution
  return [
    { name: '90-100分', value: distribution['90-100'] },
    { name: '80-89分', value: distribution['80-89'] },
    { name: '70-79分', value: distribution['70-79'] },
    { name: '60-69分', value: distribution['60-69'] },
    { name: '0-59分', value: distribution['0-59'] }
  ]
})

// 生命周期
onMounted(async () => {
  try {
    await loadClasses()
  } catch (error) {
    console.error('加载班级列表失败:', error)
    ElMessage.error('加载班级列表失败')
  }
})

// 方法
const loadClasses = async () => {
  try {
    classes.value = await teacherStore.fetchClasses()
  } catch (error) {
    console.error('加载班级失败:', error)
    throw error
  }
}

const handleClassChange = async (classId) => {
  if (!classId) return

  loading.value = true
  try {
    await Promise.all([
      teacherStore.fetchScoreStatistics(classId),
      teacherStore.fetchClassScores(classId)
    ])
  } catch (error) {
    console.error('加载成绩数据失败:', error)
    ElMessage.error('加载成绩数据失败')
  } finally {
    loading.value = false
  }
}

const getScoreTagType = (score) => {
  if (score === null || score === undefined) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

const getStatusTagType = (status) => {
  const statusMap = {
    'reviewed': 'success',
    'submitted': 'primary',
    'draft': 'info',
    '未提交': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusText = {
    'reviewed': '已批阅',
    'submitted': '已提交',
    'draft': '草稿',
    '未提交': '未提交'
  }
  return statusText[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const viewReportDetails = (report) => {
  selectedReport.value = report
  reportDialogVisible.value = true
}
</script>

<style scoped>
.score-management {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.content {
  margin-top: 20px;
}

.statistics-section {
  margin-bottom: 30px;
}

.chart-container {
  background: rgba(255, 255, 255, 0.08);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  text-align: center;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.stat-item {
  padding: 10px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: rgba(255, 255, 255, 0.9);
}

.scores-list {
  margin-top: 30px;
}

.empty-state {
  margin-top: 100px;
  text-align: center;
}

.score-management ::v-deep(.el-card) {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.score-management ::v-deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.score-management ::v-deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
}

.score-management ::v-deep(.el-table th) {
  background: #f5f7fa;
  color: #333;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
}

.score-management ::v-deep(.el-table td) {
  background: #fff;
  color: #333;
  border-bottom: 1px solid #ebeef5;
}

.score-management ::v-deep(.el-table tr:hover td) {
  background: #f5f7fa;
}

.score-management ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.score-management ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.score-management ::v-deep(.el-button--primary) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
}

.score-management ::v-deep(.el-button--primary:hover) {
  background: rgba(102, 126, 234, 0.5);
  border-color: rgba(102, 126, 234, 0.7);
}

.score-management ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.score-management ::v-deep(.el-dialog__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.score-management ::v-deep(.el-dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.score-management ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.score-management ::v-deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.8);
}

.score-management ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.score-management ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.score-management ::v-deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.score-management ::v-deep(.el-tag) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.score-management ::v-deep(.el-tag--success) {
  background: rgba(103, 194, 58, 0.1);
  border-color: rgba(103, 194, 58, 0.2);
  color: rgba(103, 194, 58, 0.8);
}

.score-management ::v-deep(.el-tag--primary) {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.2);
  color: rgba(64, 158, 255, 0.8);
}

.score-management ::v-deep(.el-tag--warning) {
  background: rgba(230, 162, 60, 0.1);
  border-color: rgba(230, 162, 60, 0.2);
  color: rgba(230, 162, 60, 0.8);
}

.score-management ::v-deep(.el-tag--danger) {
  background: rgba(245, 108, 108, 0.1);
  border-color: rgba(245, 108, 108, 0.2);
  color: rgba(245, 108, 108, 0.8);
}

.score-management ::v-deep(.el-tag--info) {
  background: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.score-management ::v-deep(.el-empty__description) {
  color: rgba(255, 255, 255, 0.7);
}
</style>
