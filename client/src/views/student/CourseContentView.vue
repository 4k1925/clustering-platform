<template>
  <div class="content-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程资料</span>
        </div>
      </template>

      <div v-if="!contents|| contents.length === 0" class="empty-state">
        <el-empty description="暂无课程资料" />
      </div>

      <div v-else class="content-list">
        <el-card
          v-for="content in contents"
          :key="content.content_id"
          class="content-card"
          shadow="hover"
        >
          <template #header>
            <div class="content-header">
              <h3>{{ content.title }}</h3>
              <div class="content-meta">
                <el-tag :type="getContentTypeTag(content.content_type)">
                  {{ getContentTypeName(content.content_type) }}
                </el-tag>
                <span class="create-time">{{ formatDate(content.created_at) }}</span>
              </div>
            </div>
          </template>

          <div class="content-body">
            <!-- 文件类型 -->
            <div v-if="content.content_type === 'file'" class="file-content">
              <el-icon><Document /></el-icon>
              <div class="file-info">
                <span>{{ content.file_name }}</span>
                <small>{{ formatFileSize(content.file_size) }}</small>
              </div>
              <el-button
                type="primary"
                size="small"
                @click="downloadFile(content.content_id)"
              >
                下载
              </el-button>
            </div>

            <!-- 视频类型 -->
            <div v-else-if="content.content_type === 'video'" class="video-content">
              <video :src="content.video_url" controls class="video-player"></video>
            </div>

            <!-- 文章类型 -->
            <div v-else-if="content.content_type === 'article'" class="article-content">
              <p>{{ content.body }}</p>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import studentApi from '@/api/student'

const contents = ref([])

onMounted(() => {
  loadContents()
})

const loadContents = async () => {
  try {
    const data = await studentApi.getContents(1) // 假设班级ID为1
    console.log('API返回的数据:', data) // 添加调试信息

    // 确保赋值的是数组
    contents.value = Array.isArray(data) ? data : []
    console.log('设置后的contents:', contents.value)
  } catch (error) {
    console.error('加载内容失败:', error)
    ElMessage.error('加载课程资料失败')
    contents.value = [] // 确保错误时也设置为空数组
  }
}

const downloadFile = async (contentId) => {
  try {
    const response = await studentApi.downloadFile(contentId)  // 使用新的下载方法
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = contents.value.find(c => c.content_id === contentId)?.file_name || 'download'
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载文件失败:', error)
    ElMessage.error('下载文件失败')
  }
}
const getContentTypeTag = (type) => {
  const map = { video: 'danger', article: 'success', file: 'warning', code: 'info' }
  return map[type] || 'info'
}

const getContentTypeName = (type) => {
  const map = {
    video: '视频',
    article: '文章',
    file: '文件',
    code: '代码示例'
  }
  return map[type] || '未知'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
<style scoped>
.course-content {
  padding: 20px;
}

.course-content ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.course-content ::v-deep(.el-card__header) {
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

.card-header span {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.search-bar {
  margin-bottom: 20px;
  padding: 0 20px;
}

.search-bar ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
}

.search-bar ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.content-item {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.content-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.content-header h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.content-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.course-content ::v-deep(.el-tag) {
  border: none;
  font-weight: 500;
}

.course-content ::v-deep(.el-tag.el-tag--danger) {
  background: rgba(245, 108, 108, 0.2);
  color: #f56c6c;
}

.course-content ::v-deep(.el-tag.el-tag--success) {
  background: rgba(103, 194, 58, 0.2);
  color: #67c23a;
}

.course-content ::v-deep(.el-tag.el-tag--warning) {
  background: rgba(230, 162, 60, 0.2);
  color: #e6a23c;
}

.create-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.content-body {
  padding: 0 20px 20px;
}

.video-wrapper {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  border-radius: 12px;
  margin-bottom: 20px;
}

.video-wrapper iframe,
.video-wrapper video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.article-body {
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  white-space: pre-wrap;
  font-size: 14px;
  margin-bottom: 20px;
}

.code-content pre {
  background: rgba(255, 255, 255, 0.05);
  padding: 20px;
  border-radius: 12px;
  overflow-x: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 20px;
}

.code-content code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.attachments {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.attachments h4 {
  margin: 0 0 15px 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  font-weight: 600;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.course-content ::v-deep(.el-link) {
  color: #667eea;
  font-weight: 500;
}

.course-content ::v-deep(.el-link:hover) {
  color: #9b59b6;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.empty-state ::v-deep(.el-empty__description) {
  color: rgba(255, 255, 255, 0.6);
}

.empty-state ::v-deep(.el-empty__image) {
  opacity: 0.5;
}

.loading-state {
  padding: 20px;
}
</style>
