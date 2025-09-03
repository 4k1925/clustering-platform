<template>
  <div class="recommendations-sidebar">
    <h3 class="recommendations-title">
      <el-icon><Star /></el-icon>
      推荐视频
    </h3>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="recommendations.length > 0" class="recommendations-list">
      <div
        v-for="rec in recommendations"
        :key="rec.id"
        class="recommendation-item"
        @click="handleRecommendationClick(rec)"
      >
        <div class="rec-thumbnail">
          <el-icon><VideoPlay /></el-icon>
        </div>
        <div class="rec-info">
          <div class="rec-title">{{ rec.title }}</div>
          <div class="rec-reason">
            <el-tag size="small" type="info">{{ rec.recommend_reason }}</el-tag>
            <span v-if="rec.matched_tags.length > 0">
              匹配标签: {{ rec.matched_tags.join(', ') }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-recommendations">
      <el-empty description="暂无推荐视频" :image-size="80" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Star, VideoPlay } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import studentApi from '@/api/student'

const props = defineProps({
  currentVideoId: {
    type: Number,
    required: true
  }
})

const router = useRouter()
const recommendations = ref([])
const loading = ref(false)

const loadRecommendations = async () => {
  loading.value = true
  try {
    const response = await studentApi.getVideoRecommendations(props.currentVideoId)
    recommendations.value = response.data
  } catch (error) {
    console.error('获取推荐视频失败:', error)
    recommendations.value = []
  } finally {
    loading.value = false
  }
}

const handleRecommendationClick = (video) => {
  // 跳转到视频详情页，传递视频ID
  router.push({
    name: 'VideoDetail',
    params: { id: video.id },
    query: { from: 'recommendation' }
  })
}

onMounted(() => {
  loadRecommendations()
})

// 监听currentVideoId变化
defineExpose({ loadRecommendations })
</script>

<style scoped>
.recommendations-sidebar {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.recommendations-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommendation-item:hover {
  background: rgba(102, 126, 234, 0.15);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(4px);
}

.rec-thumbnail {
  width: 60px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rec-thumbnail .el-icon {
  color: white;
  font-size: 20px;
}

.rec-info {
  flex: 1;
  min-width: 0;
}

.rec-title {
  color: #fff;
  font-weight: 500;
  font-size: 14px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rec-reason {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.rec-reason .el-tag {
  background: rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

.loading-state {
  padding: 20px 0;
}

.empty-recommendations {
  padding: 20px 0;
  text-align: center;
}
</style>
