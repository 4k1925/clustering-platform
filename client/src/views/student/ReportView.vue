<template>
  <div class="report-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>实验报告管理</h2>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            上传报告
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="草稿箱" name="drafts">
          <el-table :data="draftReports" style="width: 100%" v-loading="loading">
            <el-table-column v-if="draftReports.length === 0" type="empty">
              <template #default>
                <div class="empty-state">
                  <el-icon><Document /></el-icon>
                  <p>暂无草稿报告</p>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="报告名称" width="250" />
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
            <el-table-column prop="created_at" label="上传时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="downloadReport(row)" :icon="Download">
                  下载
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  @click="handleSubmitReport(row.report_id)"
                  :icon="Upload"
                >
                  提交
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  @click="handleDeleteReport(row.report_id)"
                  :icon="Delete"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="已提交" name="submitted">
          <el-table :data="submittedReports" style="width: 100%" v-loading="loading">
            <el-table-column prop="title" label="报告名称" width="250" />
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
            <el-table-column prop="submitted_at" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.submitted_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small">
                  {{ statusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="80">
              <template #default="{ row }">
                <span :class="{ 'score-text': row.score !== null }">
                  {{ row.score !== null ? row.score : '--' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="downloadReport(row)" :icon="Download">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 上传报告对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '更新报告' : '上传报告'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="currentReport" label-width="80px">
        <el-form-item label="报告标题" required>
          <el-input
            v-model="currentReport.title"
            placeholder="请输入报告标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="报告文件" required>
          <el-upload
            class="file-uploader"
            :auto-upload="false"
            :on-change="handleFileChange"
            :before-remove="handleFileRemove"
            :limit="1"
            :file-list="fileList"
            accept=".doc,.docx,.pdf,.wps,.txt,.md,.zip,.rar"
          >
            <el-button type="primary" :icon="Upload">
              选择文件
            </el-button>
            <template #tip>
              <div class="upload-tip">
                支持格式：Word(.doc/.docx)、PDF(.pdf)、WPS(.wps)、文本文件(.txt/.md)、压缩包(.zip/.rar)
              </div>
            </template>
          </el-upload>
          <div v-if="currentFile" class="file-info">
            <el-icon><Document /></el-icon>
            <span class="file-name">{{ currentFile.name }}</span>
            <span class="file-size">({{ formatFileSize(currentFile.size) }})</span>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveReport" :loading="saving">
          {{ isEditing ? '更新报告' : '上传报告' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Upload, Download, Document } from '@element-plus/icons-vue'
import { getReports, createReport, updateReport, submitReport, deleteReport } from '@/api/report'
import { formatDate } from '@/utils/helpers'

const activeTab = ref('drafts')
const showDialog = ref(false)
const isEditing = ref(false)
const loading = ref(false)
const saving = ref(false)
const currentFile = ref(null)
const fileList = ref([])
const reports = ref([])

const currentReport = ref({
  id: null,
  title: '',
  file: null
})

const draftReports = computed(() =>
  Array.isArray(reports.value) ? reports.value.filter(r => r.status === 'draft') : []
)

const submittedReports = computed(() =>
  Array.isArray(reports.value) ? reports.value.filter(r => r.status === 'submitted' || r.status === 'reviewed') : []
)


const statusText = (status) => {
  const statusMap = {
    draft: '草稿',
    submitted: '已提交',
    reviewed: '已批阅'
  }
  return statusMap[status] || status
}

const statusTagType = (status) => {
  const typeMap = {
    draft: 'info',
    submitted: 'warning',
    reviewed: 'success'
  }
  return typeMap[status] || ''
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
const fetchReports = async () => {
  loading.value = true
  try {
    const response = await getReports()
    console.log('API响应数据:', response)

    // 确保 reports.value 始终是数组
    if (Array.isArray(response)) {
      reports.value = response
    } else {
      console.warn('API返回的数据不是数组，已转换为空数组:', response)
      reports.value = []
    }

    console.log('处理后的报告数据:', reports.value)
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
    reports.value = [] // 确保始终是数组
  } finally {
    loading.value = false
  }
}
const showCreateDialog = () => {
  currentReport.value = { id: null, title: '', file: null }
  currentFile.value = null
  fileList.value = []
  isEditing.value = false
  showDialog.value = true
}

const handleFileChange = (file) => {
  currentFile.value = file.raw
  currentReport.value.file = file.raw
  // 如果未填写标题，使用文件名作为默认标题
  if (!currentReport.value.title) {
    const fileName = file.name
    const dotIndex = fileName.lastIndexOf('.')
    currentReport.value.title = dotIndex > 0 ? fileName.substring(0, dotIndex) : fileName
  }
}

const handleFileRemove = () => {
  currentFile.value = null
  currentReport.value.file = null
  fileList.value = []
  return true
}

const saveReport = async () => {
  if (!currentReport.value.title) {
    ElMessage.warning('请填写报告标题')
    return
  }

  if (!currentReport.value.file) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  saving.value = true
  try {
    const formData = new FormData()
    formData.append('title', currentReport.value.title)
    formData.append('file', currentReport.value.file)

    let response
    if (isEditing.value) {
      response = await updateReport(currentReport.value.id, formData)
      ElMessage.success('报告更新成功')
    } else {
      response = await createReport(formData)
      ElMessage.success('报告上传成功（草稿）')
    }

    // 检查响应数据
    console.log('创建/更新响应:', response.data)

    showDialog.value = false
    await fetchReports()  // 重新获取列表
  } catch (error) {
    console.error('保存报告失败:', error)
    ElMessage.error('保存报告失败: ' + (error.response?.data?.error || error.message))
  } finally {
    saving.value = false
  }
}

const handleSubmitReport = async (reportId) => {
  try {
    // 添加调试信息，确认 reportId 是否正确传递
    console.log('准备提交的报告ID:', reportId)

    if (!reportId) {
      ElMessage.error('报告ID不存在，无法提交')
      return
    }

    await ElMessageBox.confirm('确定要提交该报告吗？提交后不能修改', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 这里调用提交接口，将草稿变为已提交状态
    await submitReport(reportId) // 确保这里传递的是正确的 reportId
    ElMessage.success('报告提交成功')
    await fetchReports() // 重新获取列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交报告失败:', error)
      ElMessage.error('提交报告失败: ' + (error.response?.data?.error || error.message))
    }
  }
}


const handleDeleteReport = async (reportId) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗？此操作不可恢复', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteReport(reportId)
    ElMessage.success('报告删除成功')
    await fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除报告失败')
    }
  }
}

const downloadReport = (report) => {
  // 实际项目中应该调用下载接口
  if (report.file_url) {
    window.open(report.file_url, '_blank')
  } else {
    ElMessage.info('文件下载链接不存在')
  }
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.report-view {
  padding: 20px;
  min-height: calc(100vh - 40px);
}

.report-view ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow: 
    0 25px 50极光 rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.report-view ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-header h2 {
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 24px;
  font-weight: 600;
}

.report-view ::v-deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  border: none;
  border-radius: 12px;
  height: 40px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.report-view ::v-deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.custom-tabs {
  margin-top: 20px;
}

.report-view ::v-deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.1);
}

.report-view ::v-deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  transition: all 0.3s ease;
}

.report-view ::v-deep(.极光-tabs__item:hover) {
  color: #fff;
}

.report-view ::v-deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.report-view ::v-deep(.el-tabs__active-bar) {
  background-color: #667eea;
}

.report-view ::v-deep(.el-table) {
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

.report-view ::v-deep(.el-table th) {
  background: rgba(255, 255, 255, 0.1);
  color: #333;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.report-view ::v-deep(.el-table td) {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.report-view ::v-deep(.el-table tr:hover td) {
  background: rgba(102, 126, 234, 0.1);
}

.file-name {
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.file-size {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}

.score-text {
  font-weight: bold;
  color: #67c23a;
}

.report-view ::v-deep(.el-button) {
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  color: #000;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.report-view ::v-deep(.el-button:hover) {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.report-view ::v-deep(.el-button--danger) {
  background: #fef0f0;
  border-color: #fbc4c4;
  color: #f56c6c;
}

.report-view ::v-deep(.el-button--danger:hover) {
  background: #f56c6c;
  border-color: #f56c6c;
  color: #fff;
}

.file-uploader {
  width: 100%;
}

.upload-tip {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #ebeef5;
}

.file-info .el-icon {
  color: #409eff;
}

.file-name {
  color: #333;
  font-weight: 500;
}

.file-size {
  color: #666;
  font-size: 12px;
}

.empty-state {
  text-align: center;
  padding: 40极光 0;
  color: #666;
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
  color: #666;
}

.report-view ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-view ::v-deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
}

.report-view ::v-deep(.el-dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.report-view ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: #333;
}

.report-view ::v-deep(.el-form-item__label) {
  color: #333;
  font-weight: 500;
}

.report-view ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.report-view ::v-deep(.el-input__inner) {
  color: #333;
  font-weight: 500;
}

.report-view ::v-deep(.el-upload) {
  width: 100%;
}

.report-view ::v-deep(.el-upload .el-button) {
  width: 100%;
  justify-content: center;
}



</style>
