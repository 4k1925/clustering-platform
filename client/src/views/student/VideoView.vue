<template>
  <div class="video-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教学视频</span>
          <el-button type="primary" @click="loadVideos" :loading="loading">
            刷新视频列表
          </el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="videos.length === 0" class="empty-state">
        <el-empty description="暂无视频内容" />
      </div>

      <div v-else class="video-list">
        <el-card
          v-for="video in videos"
          :key="video.content_id"
          class="video-card"
          shadow="hover"
        >
          <template #header>
            <div class="video-header">
              <h3>{{ video.title }}</h3>
              <div class="video-meta">
                <el-tag type="success">视频</el-tag>
                <span class="class-name">{{ video.class_name || '未分类' }}</span>
                <span class="create-time">{{ formatDate(video.created_at) }}</span>
              </div>
            </div>
          </template>

          <div class="video-content">
            <div v-if="video.video_url" class="video-player">
              <video
                :src="getFullVideoUrl(video.video_url)"
                controls
                class="video-element"
                :data-video-id="video.content_id"
                @play="recordWatchHistory(video.content_id)"
              ></video>
            </div>
            <div v-else class="no-video">
              <el-icon><VideoCamera /></el-icon>
              <p>视频链接无效或未设置</p>
            </div>

            <div v-if="video.description" class="video-description">
              <p>{{ video.description }}</p>
            </div>

            <!-- 推荐视频区域 -->
            <div v-if="video.recommendations && video.recommendations.length > 0" class="recommendations">
              <h4>相关推荐</h4>
              <div class="recommendation-list">
                <el-tag
                  v-for="rec in video.recommendations"
                  :key="rec.content_id"
                  type="info"
                  class="recommendation-tag"
                  @click="goToVideoDetail(rec.content_id)"
                >
                  {{ rec.title }}
                </el-tag>
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
import { VideoCamera } from '@element-plus/icons-vue'
import studentApi from '@/api/student'
import { useRouter } from 'vue-router'

const videos = ref([])
const loading = ref(false)
const router = useRouter()

onMounted(() => {
  loadVideos()
})

const loadVideos = async () => {
  loading.value = true
  try {
    const response = await studentApi.getVideos()
    // 处理响应数据
    if (response && response.data) {
      videos.value = response.data.map(video => ({
        content_id: video.id,
        title: video.title,
        description: video.description,
        video_url: video.file_path,
        created_at: video.upload_time,
        class_name: video.course_name
      }))
    } else {
      videos.value = []
    }
    console.log('视频数据加载成功:', videos.value)
  } catch (error) {
    console.error('加载视频失败:', error)
    ElMessage.error('加载视频失败')
    videos.value = []
  } finally {
    loading.value = false
  }
}

const getFullVideoUrl = (url) => {
  if (!url) return ''
  // 如果是相对路径，添加基础URL
  if (url.startsWith('/')) {
    return `http://localhost:5000${url}`
  }
  return url
}

const recordWatchHistory = async (videoId) => {
  try {
    // 获取视频元素，计算当前播放进度
    const videoElement = document.querySelector(`video[data-video-id="${videoId}"]`)
    let progress = 0
    if (videoElement) {
      progress = Math.floor((videoElement.currentTime / videoElement.duration) * 100)
    }
    await studentApi.recordWatchHistory(videoId, progress)
    console.log(`记录视频 ${videoId} 观看进度: ${progress}%`)
  } catch (error) {
    console.error('记录观看历史失败:', error)
  }
}

const goToVideoDetail = (videoId) => {
  router.push({ name: 'VideoDetail', params: { id: videoId } })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>
<style scoped>
.video-view {
  padding: 20px;
}

.video-view ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow:
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.video-view ::v-deep(.el-card__header) {
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

.video-view ::v-deep(.el-select) {
  width: 200px;
}

.video-view ::v-deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
}

.video-view ::v-deep(.el-select .el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.video-view ::v-deep(.el-select .el-input__suffix) {
  color: rgba(255, 255, 255, 0.7);
}

.video-view ::v-deep(.el-select-dropdown) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.video-view ::v-deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
}

.video-view ::v-deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
}

.video-view ::v-deep(.el-select-dropdown__item.selected) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.video-item {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.video-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.video-header h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.create-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.video-content {
  padding: 0 20px 20px;
}

.video-player {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
}

.video-player iframe,
.video-player video {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.video-description p {
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 14px;
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
