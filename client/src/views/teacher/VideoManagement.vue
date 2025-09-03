<template>
  <div class="video-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <el-button type="primary" @click="showUploadDialog">上传视频</el-button>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="!videos || videos.length === 0" class="empty-state">
        <el-empty description="暂无视频" />
      </div>

      <div v-else class="video-list">
        <el-table :data="videos" style="width: 100%">
          <el-table-column prop="title" label="标题" min-width="200" />
          <el-table-column prop="description" label="描述" min-width="300" show-overflow-tooltip />
          <el-table-column prop="upload_time" label="上传时间" width="180" />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" @click="editVideo(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 上传视频对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传视频" width="500px">
      <el-form :model="videoForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="videoForm.title" placeholder="请输入视频标题" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="videoForm.description" type="textarea" :rows="3" placeholder="请输入视频描述" />
        </el-form-item>

        <el-form-item label="视频文件" required>
          <el-upload
            class="video-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            :data="{ course_id: currentClassId, title: videoForm.title, description: videoForm.description }"
            :show-file-list="false"
            accept="video/*"
          >
            <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
              <el-progress :percentage="uploadProgress" />
            </div>
            <div v-else class="upload-trigger">
              <el-icon><Upload /></el-icon>
              <div class="upload-text">点击上传视频</div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="uploadVideo" :disabled="!videoForm.file">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑视频对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑视频" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" placeholder="请输入视频标题" />
        </el-form-item>

        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入视频描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateVideo">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import axios from 'axios'
import { getToken } from '@/utils/auth'

const route = useRoute()
const currentClassId = computed(() => route.query.class_id)

const videos = ref([])
const loading = ref(true)
const uploadDialogVisible = ref(false)
const editDialogVisible = ref(false)
const uploadProgress = ref(0)

const videoForm = ref({
  title: '',
  description: '',
  file: null
})

const editForm = ref({
  id: null,
  title: '',
  description: ''
})

const uploadUrl = '/api/teacher/videos/upload'
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${getToken()}`
}))

onMounted(() => {
  if (currentClassId.value) {
    loadVideos()
  }
})

const loadVideos = async () => {
  if (!currentClassId.value) {
    ElMessage.warning('请先选择班级')
    return
  }

  loading.value = true
  try {
    const response = await axios.get(`/api/teacher/videos?class_id=${currentClassId.value}`)
    videos.value = response.data
  } catch (error) {
    console.error('加载视频失败:', error)
    ElMessage.error('加载视频列表失败')
  } finally {
    loading.value = false
  }
}

const showUploadDialog = () => {
  if (!currentClassId.value) {
    ElMessage.warning('请先选择班级')
    return
  }

  videoForm.value = {
    title: '',
    description: '',
    file: null
  }
  uploadProgress.value = 0
  uploadDialogVisible.value = true
}

const beforeUpload = (file) => {
  const isVideo = file.type.startsWith('video/')
  const isLt500M = file.size / 1024 / 1024 < 500

  if (!isVideo) {
    ElMessage.error('请上传视频文件!')
    return false
  }

  if (!isLt500M) {
    ElMessage.error('视频大小不能超过500MB!')
    return false
  }

  videoForm.value.file = file
  return true
}

const handleUploadProgress = (event) => {
  uploadProgress.value = Math.round((event.loaded * 100) / event.total)
}

const handleUploadSuccess = () => {
  uploadProgress.value = 100
  uploadDialogVisible.value = false
  ElMessage.success('视频上传成功')
  loadVideos()
}

const handleUploadError = (error) => {
  uploadProgress.value = 0
  console.error('上传失败:', error)
  ElMessage.error('视频上传失败')
}

const uploadVideo = () => {
  if (!videoForm.value.title) {
    ElMessage.warning('请输入视频标题')
    return
  }

  if (!videoForm.value.file) {
    ElMessage.warning('请选择视频文件')
    return
  }

  const formData = new FormData()
  formData.append('file', videoForm.value.file)
  formData.append('title', videoForm.value.title)
  formData.append('description', videoForm.value.description || '')
  formData.append('course_id', currentClassId.value)

  axios.post(uploadUrl, formData, {
    headers: {
      ...uploadHeaders.value,
      'Content-Type': 'multipart/form-data'
    },
    onUploadProgress: handleUploadProgress
  })
  .then(handleUploadSuccess)
  .catch(handleUploadError)
}

const editVideo = (video) => {
  editForm.value = {
    id: video.id,
    title: video.title,
    description: video.description || ''
  }
  editDialogVisible.value = true
}

const updateVideo = async () => {
  if (!editForm.value.title) {
    ElMessage.warning('请输入视频标题')
    return
  }

  try {
    await axios.put(`/api/teacher/videos/${editForm.value.id}`, {
      title: editForm.value.title,
      description: editForm.value.description
    })

    ElMessage.success('视频信息更新成功')
    editDialogVisible.value = false
    loadVideos()
  } catch (error) {
    console.error('更新视频信息失败:', error)
    ElMessage.error('更新视频信息失败')
  }
}

const confirmDelete = (video) => {
  ElMessageBox.confirm(
    '确定要删除这个视频吗？此操作不可恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  .then(async () => {
    try {
      await axios.delete(`/api/teacher/videos/${video.id}`)
      ElMessage.success('视频已删除')
      loadVideos()
    } catch (error) {
      console.error('删除视频失败:', error)
      ElMessage.error('删除视频失败')
    }
  })
  .catch(() => {
    // 用户取消删除
  })
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container {
  padding: 20px 0;
}

.empty-state {
  padding: 40px 0;
  text-align: center;
}

.video-uploader {
  width: 100%;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
}

.upload-text {
  margin-top: 10px;
  color: #606266;
}

.upload-progress {
  padding: 20px;
}
</style>
