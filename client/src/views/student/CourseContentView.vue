<template>
  <div class="course-content">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程资料</span>
          <el-select v-model="selectedClass" placeholder="选择班级" @change="loadContents">
            <el-option
              v-for="classItem in classes"
              :key="classItem.class_id"
              :label="classItem.name"
              :value="classItem.class_id"
            />
          </el-select>
        </div>
      </template>

      <div v-if="contents.length === 0" class="empty-state">
        <el-empty description="暂无课程资料" />
      </div>

      <div v-else class="content-list">
        <el-card
          v-for="content in contents"
          :key="content.content_id"
          class="content-item"
        >
          <template #header>
            <div class="content-header">
              <h3>{{ content.title }}</h3>
              <div class="content-meta">
                <el-tag :type="getContentTypeTag(content.content_type)">
                  {{ getContentTypeText(content.content_type) }}
                </el-tag>
                <span class="create-time">{{ formatTime(content.created_at) }}</span>
              </div>
            </div>
          </template>

          <div class="content-body">
            <div v-if="content.content_type === 'video' && content.video_url" class="video-content">
              <div class="video-wrapper">
                <iframe
                  v-if="isYouTubeUrl(content.video_url)"
                  :src="getYouTubeEmbedUrl(content.video_url)"
                  width="100%"
                  height="400"
                  frameborder="0"
                  allowfullscreen
                ></iframe>
                <video
                  v-else
                  :src="content.video_url"
                  controls
                  width="100%"
                  height="400"
                ></video>
              </div>
            </div>

            <div v-else-if="content.content_type === 'article'" class="article-content">
              <div class="article-body">{{ content.body }}</div>
            </div>

            <div v-else-if="content.content_type === 'code_example'" class="code-content">
              <pre><code>{{ content.body }}</code></pre>
            </div>

            <div v-if="content.attachments" class="attachments">
              <h4>附件：</h4>
              <div class="attachment-list">
                <el-link
                  v-for="(attachment, index) in parseAttachments(content.attachments)"
                  :key="index"
                  :href="attachment.url"
                  target="_blank"
                  type="primary"
                >
                  {{ attachment.name }}
                </el-link>
              </div>
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
import studentApi from '@/api/student'

const classes = ref([])
const contents = ref([])
const selectedClass = ref(null)

onMounted(async () => {
  try {
    await loadClasses()
  } catch (error) {
    console.error('初始化失败:', error)
    ElMessage.error('加载失败')
  }
})

const loadClasses = async () => {
  try {
    const response = await studentApi.getClasses()
    classes.value = response.data
  } catch (error) {
    console.error('获取班级失败:', error)
    ElMessage.error('获取班级列表失败')
  }
}

const loadContents = async () => {
  if (!selectedClass.value) {
    contents.value = []
    return
  }
  
  try {
    const response = await studentApi.getContents(selectedClass.value)
    contents.value = response.data
  } catch (error) {
    console.error('获取内容失败:', error)
    ElMessage.error('获取课程资料失败')
  }
}

const getContentTypeTag = (type) => {
  const map = {
    video: 'danger',
    article: 'success',
    code_example: 'warning'
  }
  return map[type] || ''
}

const getContentTypeText = (type) => {
  const map = {
    video: '视频',
    article: '文章',
    code_example: '代码示例'
  }
  return map[type] || type
}

const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN')
}

const isYouTubeUrl = (url) => {
  return url.includes('youtube.com') || url.includes('youtu.be')
}

const getYouTubeEmbedUrl = (url) => {
  if (url.includes('youtube.com')) {
    const videoId = url.split('v=')[1]?.split('&')[0]
    return videoId ? `https://www.youtube.com/embed/${videoId}` : url
  } else if (url.includes('youtu.be')) {
    const videoId = url.split('/').pop()
    return videoId ? `https://www.youtube.com/embed/${videoId}` : url
  }
  return url
}

const parseAttachments = (attachments) => {
  if (!attachments) return []
  
  try {
    if (typeof attachments === 'string') {
      return attachments.split(',').map(item => {
        const [name, url] = item.split('|')
        return { name: name.trim(), url: url.trim() }
      })
    }
    return []
  } catch (error) {
    console.error('解析附件失败:', error)
    return []
  }
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
    inset 0 0 20px rgba(255, 255, 255, 极光.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.course-content ::v-deep(.极光-card__header) {
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

.course-content ::v-deep(.el-select) {
  width: 200px;
}

.course-content ::v-deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
}

.course-content ::v-deep(.el-select .el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.course-content ::v-deep(.el-select .el-input__suffix) {
  color: rgba(255, 255, 255, 0.7);
}

.course-content ::v-deep(.el-select-dropdown) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.course-content ::v-deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
}

.course-content ::v-deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
}

.course-content ::v-deep(.el-select-dropdown__item.selected) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
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
</style>
