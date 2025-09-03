<template>
  <div class="video-detail-view">
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <span class="header-title">视频详情</span>
      </template>
    </el-page-header>

    <div class="video-container">
      <!-- 左侧视频播放区域 -->
      <div class="video-main">
        <el-card class="video-player-card">
          <template #header>
            <div class="video-header">
              <h2>{{ currentVideo.title }}</h2>
              <div class="video-meta">
                <el-tag type="success">视频</el-tag>
                <span class="create-time">{{ formatDate(currentVideo.created_at) }}</span>
              </div>
            </div>
          </template>

          <div class="video-content">
            <video
              ref="videoPlayer"
              :src="currentVideo.url"
              controls
              class="video-player"
              @timeupdate="handleTimeUpdate"
            ></video>
            
            <div class="video-description" v-if="currentVideo.description">
              <h4>视频描述</h4>
              <p>{{ currentVideo.description }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右侧推荐侧边栏 -->
      <div class="video-sidebar">
        <VideoRecommendations :current-video-id="parseInt($route.params.id)" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import VideoRecommendations from '@/components/clustering/VideoRecommendations.vue'
import studentApi from '@/api/student'

const route = useRoute()
const router = useRouter()
const videoPlayer = ref(null)
const currentVideo = ref({})
const lastRecordedTime = ref(0)

const loadVideoDetail = async () => {
  try {
    const response = await studentApi.getVideo(parseInt(route.params.id))
    currentVideo.value = response.data
  } catch (error) {
    console.error('加载视频详情失败:', error)
    ElMessage.error('加载视频失败')
  }
}

const handleTimeUpdate = () => {
  if (!videoPlayer.value) return
  
  const currentTime = Math.floor(videoPlayer.value.currentTime)
  // 每10秒记录一次观看进度
  if (currentTime - lastRecordedTime.value >= 10) {
    studentApi.recordWatchHistory(parseInt(route.params.id), 10)
    lastRecordedTime.value = currentTime
  }
}

const goBack = () => {
  router.push({ name: 'VideoView' })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

onMounted(() => {
  loadVideoDetail()
})

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadVideoDetail()
    lastRecordedTime.value = 0
  }
})
</script>

<style scoped>
.video-detail-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header ::v-deep(.el-page-header__content) {
  color: #fff;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
}

.video-container {
  display: flex;
  gap: 20px;
}

.video-main {
  flex: 3;
}

.video-sidebar {
  flex: 1;
  min-width: 300px;
}

.video-player-card {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.video-player-card ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-header h2 {
  margin: 0;
  color: #fff;
  font-size: 20px;
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
  padding: 20px;
}

.video-player {
  width: 100%;
  height: 400px;
  border-radius: 12px;
  background: #000;
  margin-bottom: 20px;
}

.video-description h4 {
  color: #fff;
  margin: 0 0 10px 0;
  font-size: 16px;
}

.video-description p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
}
</style>