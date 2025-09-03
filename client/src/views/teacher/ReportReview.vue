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
        <el-table-column prop="file_name" label="文件名" width="200">
          <template #default="{ row }">
            <span class="file-name">{{ row.file_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="downloadReport(scope.row)">下载</el-button>
            <el-button size="small" type="primary" @click="reviewReport(scope.row)">批阅</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 批阅报告对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="报告批阅" width="80%">
      <div class="report-container">
        <h2>{{ currentReport.title }}</h2>
        <div class="report-meta">
          <div class="meta-item">
            <strong>学生:</strong> {{ currentReport.author?.username }}
          </div>
          <div class="meta-item">
            <strong>提交时间:</strong> {{ formatDate(currentReport.created_at) }}
          </div>
          <div class="meta-item">
            <strong>文件:</strong> {{ currentReport.file_name }}
          </div>
          <div class="meta-item">
            <strong>大小:</strong> {{ formatFileSize(currentReport.file_size) }}
          </div>
          <div class="meta-item">
            <strong>类型:</strong> {{ currentReport.file_type?.toUpperCase() }}
          </div>
        </div>

        <!-- 文件操作区域 -->
        <div class="file-actions">
          <el-button
            type="primary"
            @click="downloadCurrentReport"
            :icon="Download"
          >
            下载报告文件
          </el-button>

          <el-tag v-if="currentReport.file_type" type="info">
            {{ getFileTypeText(currentReport.file_type) }}
          </el-tag>
        </div>

        <el-divider />

        <!-- 文件预览提示 -->
        <div class="preview-info">
          <el-alert
            title="文件预览提示"
            type="info"
            :closable="false"
            show-icon
          >
            <p>该报告为 {{ currentReport.file_type?.toUpperCase() }} 格式文件</p>
            <p>请下载后使用相应软件查看完整内容</p>
          </el-alert>
        </div>

        <!-- 简单的文本内容显示（如果有的话） -->
        <div v-if="currentReport.content" class="content-preview">
          <h4>报告内容摘要:</h4>
          <div class="content-text">
            {{ currentReport.content }}
          </div>
        </div>

        <el-divider />

        <el-form :model="reviewForm" label-width="100px">
          <el-form-item label="评分" required>
            <el-input-number
              v-model="reviewForm.score"
              :min="0"
              :max="100"
              :step="0.5"
              placeholder="请输入0-100之间的分数"
            />
          </el-form-item>
          <el-form-item label="反馈意见">
            <el-input
              v-model="reviewForm.feedback"
              type="textarea"
              :rows="5"
              placeholder="请输入批阅反馈意见"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="reviewLoading">
          提交批阅
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'

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
const reviewLoading = ref(false)

onMounted(async () => {
  try {
    classes.value = await teacherStore.fetchClasses()
    console.log('获取到的班级列表:', classes.value)
  } catch (error) {
    console.error('获取班级列表失败:', error)
    ElMessage.error('获取班级列表失败')
  }
})

const loadReports = async () => {
  if (selectedClass.value) {
    console.log('开始加载报告，班级ID:', selectedClass.value, '状态:', reportStatus.value)
    try {
      reports.value = await teacherStore.fetchReports(selectedClass.value, reportStatus.value)
      console.log('获取到的报告数据:', reports.value)

      if (reports.value.length === 0) {
        ElMessage.info('该班级没有找到相关报告')
      }
    } catch (error) {
      console.error('加载报告失败:', error)
      ElMessage.error('加载报告失败')
    }
  } else {
    console.log('未选择班级，不加载报告')
    reports.value = []
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
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch (error) {
    console.error('日期格式化错误:', error)
    return dateString
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileTypeText = (fileType) => {
  const typeMap = {
    'doc': 'Word文档',
    'docx': 'Word文档',
    'pdf': 'PDF文档',
    'txt': '文本文件',
    'zip': '压缩文件',
    'rar': '压缩文件',
    'jpg': '图片',
    'png': '图片',
    'xlsx': 'Excel文件',
    'pptx': 'PPT文件'
  }
  return typeMap[fileType?.toLowerCase()] || '文件'
}

const downloadReport = (report) => {
  if (report.file_url) {
    // 直接打开下载链接
    window.open(report.file_url, '_blank')
    ElMessage.success('开始下载文件')
  } else {
    ElMessage.warning('文件下载链接不可用')
  }
}

const downloadCurrentReport = () => {
  downloadReport(currentReport.value)
}

const reviewReport = (report) => {
  currentReport.value = report
  reviewForm.value = {
    score: report.score || null,
    feedback: report.feedback || ''
  }
  reviewDialogVisible.value = true

  console.log('打开批阅对话框，报告信息:', report)
}

const submitReview = async () => {
  if (!reviewForm.value.score && reviewForm.value.score !== 0) {
    ElMessage.warning('请填写评分')
    return
  }

  if (reviewForm.value.score < 0 || reviewForm.value.score > 100) {
    ElMessage.warning('评分必须在0-100之间')
    return
  }

  reviewLoading.value = true
  try {
    await teacherStore.reviewReport(currentReport.value.report_id, reviewForm.value)
    ElMessage.success('批阅提交成功')
    reviewDialogVisible.value = false
    await loadReports() // 重新加载报告列表
  } catch (error) {
    console.error('批阅失败:', error)
    ElMessage.error(error.message || '批阅失败，请重试')
  } finally {
    reviewLoading.value = false
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
  flex-wrap: wrap;
  gap: 10px;
}

.card-header > div {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.report-container {
  padding: 0 20px;
}

.report-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin: 20px 0;
  padding: 15px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item strong {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 20px 0;
  padding: 15px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  border-left: 4px solid rgba(102, 126, 234, 0.5);
}

.preview-info {
  margin: 20px 0;
}

.content-preview {
  margin: 20px 0;
  padding: 15px;
  background: rgba(103, 194, 58, 0.1);
  border-radius: 8px;
  border-left: 4px solid rgba(103, 194, 58, 0.5);
}

.content-text {
  white-space: pre-wrap;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.file-name {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: rgba(102, 126, 234, 0.8);
}

.report-review ::v-deep(.el-card) {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.report-review ::v-deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.report-review ::v-deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
}

.report-review ::v-deep(.el-table th) {
  background: #f5f7fa;
  color: #333;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
}

.report-review ::v-deep(.el-table td) {
  background: #fff;
  color: #333;
  border-bottom: 1px solid #ebeef5;
}

.report-review ::v-deep(.el-table tr:hover td) {
  background: #f5f7fa;
}

.report-review ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.report-review ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.report-review ::v-deep(.el-button--primary) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
}

.report-review ::v-deep(.el-button--primary:hover) {
  background: rgba(102, 126, 234, 0.5);
  border-color: rgba(102, 126, 234, 0.7);
}

.report-review ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-review ::v-deep(.el-dialog__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.report-review ::v-deep(.el-dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.report-review ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.report-review ::v-deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.8);
}

.report-review ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.report-review ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.report-review ::v-deep(.el-input-number) {
  width: 100%;
}

.report-review ::v-deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.report-review ::v-deep(.el-alert) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-review ::v-deep(.el-alert__title) {
  color: rgba(255, 255, 255, 0.9);
}

.report-review ::v-deep(.el-alert__description) {
  color: rgba(255, 255, 255, 0.8);
}

.report-review ::v-deep(.el-tag) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.report-review ::v-deep(.el-tag--info) {
  background: rgba(144, 147, 153, 0.1);
  border-color: rgba(144, 147, 153, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.report-review ::v-deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.1);
}
</style>
