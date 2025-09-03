<template>
  <div class="video-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教学视频</span>
          <el-select v-model="selectedClass" placeholder="选择班级" @change="loadVideos">
            <el-option
              v-for="classItem in classes"
              :key="classItem.class_id"
              :label="classItem.name"
              :value="classItem.class_id"
            />
          </el-select>
        </div>
      </template>

      <div v-if="videos.length === 0" class="empty-state">
        <el-empty description="暂无教学视频" />
      </div>

      <div v-else class="video-list">
        <el-card
          v-for="video in videos"
          :key="video.content_id"
          class="video-item"
        >
          <template #header>
            <div class="video-header">
              <h3>{{ video.title }}</h3>
              <div class="video-meta">
                <span class="create-time">{{ formatTime(video.created_at) }}</span>
              </div>
            </div>
          </template>

          <div class="video-content">
            <div class="video-player">
              <iframe
                v-if="isYouTubeUrl(video.video_url)"
                :src="getYouTubeEmbedUrl(video.video_url)"
                width="100%"
                height="400"
                frameborder="0"
                allowfullscreen
              ></iframe>
              <video
                v-else
                :src="video.video_url"
                controls
                width="100%"
                height="400"
              ></video>
            </div>
            
            <div class="video-description">
              <p>{{ video.body }}</p>
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

const pageTitle = ref('教学视频')
const classes = ref([])
const videos = ref([])
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

const loadVideos = async () => {
  if (!selectedClass.value) {
    videos.value = []
    return
  }
  
  try {
    const response = await studentApi.getContents(selectedClass.value)
    videos.value = response.data.filter(item => item.content_type === 'video')
  } catch (error) {
    console.error('获取视频失败:', error)
    ElMessage.error('获取教学视频失败')
  }
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
