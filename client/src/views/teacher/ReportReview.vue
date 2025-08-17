<template>
  <div class="report-review">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>实验报告批阅</span>
          <div>
            <el-select v-model="selectedClass" placeholder="选择班级" @change="loadReports">
              <el-option
                v-for="classItem in classes"
                :key="classItem.class_id"
                :label="classItem.name"
                :value="classItem.class_id"
              />
            </el-select>
            <el-select v-model="reportStatus" placeholder="选择状态" @change="loadReports" style="margin-left: 10px;">
              <el-option label="已提交" value="submitted" />
              <el-option label="已批阅" value="reviewed" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="reports" border style="width: 100%">
        <el-table-column prop="title" label="报告标题" />
        <el-table-column prop="author.username" label="学生" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="reviewReport(scope.row)">批阅</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 批阅报告对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="报告批阅" width="70%">
      <div class="report-container">
        <h2>{{ currentReport.title }}</h2>
        <div class="report-meta">
          <span>学生: {{ currentReport.author?.username }}</span>
          <span>提交时间: {{ formatDate(currentReport.created_at) }}</span>
        </div>
        <div class="report-content" v-html="currentReport.content"></div>

        <el-divider />

        <el-form :model="reviewForm" label-width="100px">
          <el-form-item label="评分" required>
            <el-input-number v-model="reviewForm.score" :min="0" :max="100" :step="0.5" />
          </el-form-item>
          <el-form-item label="反馈">
            <el-input v-model="reviewForm.feedback" type="textarea" :rows="5" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交批阅</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage } from 'element-plus'

const teacherStore = useTeacherStore()

const classes = ref([])
const reports = ref([])
const selectedClass = ref(null)
const reportStatus = ref('submitted')
const reviewDialogVisible = ref(false)
const currentReport = ref({})
const reviewForm = ref({
  score: null,
  feedback: ''
})

onMounted(async () => {
  classes.value = await teacherStore.fetchClasses()
})

const loadReports = async () => {
  if (selectedClass.value) {
    reports.value = await teacherStore.fetchReports(selectedClass.value, reportStatus.value)
  }
}

const getStatusTag = (status) => {
  const map = {
    draft: 'info',
    submitted: 'warning',
    reviewed: 'success',
    archived: ''
  }
  return map[status] || ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString()
}

const reviewReport = (report) => {
  currentReport.value = report
  reviewForm.value = {
    score: report.score || null,
    feedback: report.feedback || ''
  }
  reviewDialogVisible.value = true
}

const submitReview = async () => {
  try {
    if (!reviewForm.value.score) {
      ElMessage.warning('请填写评分')
      return
    }

    await teacherStore.reviewReport(currentReport.value.report_id, reviewForm.value)
    ElMessage.success('批阅提交成功')
    reviewDialogVisible.value = false
    await loadReports()
  } catch (error) {
    ElMessage.error(error.message || '批阅失败')
  }
}
</script>

<style scoped>
.report-review {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.report-container {
  padding: 0 20px;
}
.report-meta {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
  color: #666;
}
.report-content {
  margin: 20px 0;
  line-height: 1.6;
}
</style>
