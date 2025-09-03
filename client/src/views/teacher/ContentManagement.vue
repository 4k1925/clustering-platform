<template>
  <div class="content-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程内容管理</span>
          <div>
            <el-select v-model="selectedClass" placeholder="选择班级" @change="loadContents">
              <el-option
                v-for="classItem in classes"
                :key="classItem.class_id"
                :label="classItem.name"
                :value="classItem.class_id"
              />
            </el-select>
            <el-radio-group v-model="activeTab" style="margin-left: 10px;" @change="handleTabChange">
              <el-radio-button label="article">课程资料</el-radio-button>
              <el-radio-button label="video">教学视频</el-radio-button>
            </el-radio-group>
            <el-button type="primary" @click="showCreateDialog" style="margin-left: 10px;">
              {{ activeTab === 'video' ? '上传视频' : '上传资料' }}
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredContents" border style="width: 100%">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content_type" label="类型" v-if="activeTab === 'article'">
          <template #default="scope">
            <el-tag :type="getContentTypeTag(scope.row.content_type)">
              {{ getContentTypeDisplay(scope.row.content_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件" v-if="activeTab === 'article'">
          <template #default="scope">
            <div v-if="scope.row.attachments">
              <el-button
                v-for="(file, index) in parseAttachments(scope.row.attachments)"
                :key="index"
                size="small"
                type="success"
                @click="downloadFile(file.url, file.name)"
              >
                {{ file.name }}
              </el-button>
            </div>
            <span v-else style="color: #999;">无附件</span>
          </template>
        </el-table-column>
        <el-table-column label="标签" v-if="activeTab === 'video'">
          <template #default="scope">
            <div v-if="scope.row.tags && scope.row.tags.length > 0">
              <el-tag
                v-for="(tag, index) in JSON.parse(scope.row.tags || '[]')"
                :key="index"
                size="small"
                style="margin-right: 4px; margin-bottom: 4px;"
              >
                {{ tag }}
              </el-tag>
            </div>
            <span v-else style="color: #999;">无标签</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_published" label="状态">
          <template #default="scope">
            <el-tag :type="scope.row.is_published ? 'success' : 'info'">
              {{ scope.row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editContent(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteContent(scope.row.content_id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑内容对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="70%">
      <el-form :model="contentForm" label-width="100px">
        <el-form-item label="标题" required>
          <el-input v-model="contentForm.title" />
        </el-form-item>
        <el-form-item label="内容类型" required v-if="!isEditMode">
          <el-radio-group v-model="contentForm.content_type" @change="handleContentTypeChange">
            <el-radio-button :label="activeTab === 'video' ? 'video' : 'article'">
              {{ activeTab === 'video' ? '视频' : '文章资料' }}
            </el-radio-button>
            <el-radio-button v-if="activeTab === 'article'" label="code_example">代码示例</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 视频特定字段 -->
        <template v-if="contentForm.content_type === 'video'">
          <el-form-item label="视频文件" required>
            <el-upload
              class="video-uploader"
              :action="uploadUrl"
              :on-success="handleVideoUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeVideoUpload"
              :show-file-list="false"
              :headers="uploadHeaders"
            >
              <div v-if="contentForm.video_url" class="video-preview">
                <video :src="contentForm.video_url" controls style="max-width: 100%; max-height: 200px;"></video>
              </div>
              <el-button v-else type="primary">选择视频文件</el-button>
              <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
                <el-progress :percentage="uploadProgress" />
              </div>
            </el-upload>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
              支持格式：MP4、WebM等视频文件，最大100MB
            </div>
          </el-form-item>

          <el-form-item label="视频标签" required>
            <el-tag
              v-for="tag in contentForm.tags"
              :key="tag"
              closable
              size="medium"
              style="margin-right: 8px; margin-bottom: 8px;"
              @close="removeTag(tag)"
            >
              {{ tag }}
            </el-tag>
            <el-input
              v-if="inputVisible"
              ref="tagInputRef"
              v-model="inputValue"
              size="small"
              style="width: 120px;"
              @keyup.enter="handleTagInputConfirm"
              @blur="handleTagInputConfirm"
            />
            <el-button v-else size="small" @click="showTagInput">
              + 添加标签
            </el-button>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
              输入标签后按回车添加，用于视频推荐系统（如：K-Means, 聚类, 无监督学习）
            </div>
          </el-form-item>

          <el-form-item label="视频描述">
            <el-input v-model="contentForm.description" type="textarea" :rows="3" placeholder="请输入视频描述..." />
          </el-form-item>
        </template>

        <!-- 其他内容类型字段 -->
        <template v-else>
          <el-form-item label="内容描述">
            <el-input v-model="contentForm.body" type="textarea" :rows="5" placeholder="请输入详细内容描述..." />
          </el-form-item>
          <el-form-item label="资料文件">
            <el-upload
              class="file-uploader"
              :action="uploadUrl"
              :on-success="handleFileUploadSuccess"
              :on-error="handleUploadError"
              :before-upload="beforeFileUpload"
              :on-remove="handleFileRemove"
              multiple
              :file-list="fileList"
              :headers="uploadHeaders"
            >
              <el-button type="primary">选择文件</el-button>
              <div style="font-size: 12px; color: #666; margin-top: 5px;">
                支持各种文档格式：PDF、Word、Excel、PPT等，单个文件最大50MB
              </div>
            </el-upload>
          </el-form-item>
        </template>

        <el-form-item label="发布状态">
          <el-switch v-model="contentForm.is_published" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitContentForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'
import teacherApi, { videoUploadUrl, materialUploadUrl } from '@/api/teacher'

const teacherStore = useTeacherStore()

const classes = ref([])
const contents = ref([])
const selectedClass = ref(null)
const dialogVisible = ref(false)
const currentContentId = ref(null)
const inputVisible = ref(false)
const inputValue = ref('')
const tagInputRef = ref(null)
const activeTab = ref('article') // 默认显示文章资料
const fileList = ref([])
const uploadProgress = ref(0)
const isEditMode = ref(false)
const uploadUrl = computed(() => activeTab.value === 'video' ? videoUploadUrl : materialUploadUrl)
const uploadHeaders = {
  'X-Requested-With': 'XMLHttpRequest'
}

const contentForm = ref({
  title: '',
  content_type: 'article',
  body: '',
  video_url: '',
  description: '',
  tags: [], // 改为数组格式
  is_published: false,
  class_id: null
})


const dialogTitle = computed(() => {
  return currentContentId.value ? '编辑内容' : '创建内容'
})

// 根据当前选择的标签过滤内容
const filteredContents = computed(() => {
  if (activeTab.value === 'video') {
    return contents.value.filter(item => item.content_type === 'video')
  } else {
    return contents.value.filter(item => item.content_type !== 'video')
  }
})

// 获取内容类型显示名称
const getContentTypeDisplay = (type) => {
  const map = {
    video: '视频',
    article: '文章资料',
    code_example: '代码示例'
  }
  return map[type] || type
}

onMounted(async () => {
  try {
    classes.value = await teacherStore.fetchClasses()
    console.log('获取到的班级:', classes.value)

    if (!Array.isArray(teacherStore.contents)) {
      teacherStore.contents = []
    }
  } catch (error) {
    console.error('获取班级失败:', error)
    ElMessage.error('获取班级列表失败')
  }
})

// 监听activeTab变化，更新内容类型
watch(activeTab, (newVal) => {
  if (dialogVisible.value && !isEditMode.value) {
    contentForm.value.content_type = newVal === 'video' ? 'video' : 'article'
  }
})

const loadContents = async () => {
  if (selectedClass.value) {
    try {
      if (activeTab.value === 'video') {
        // 加载视频内容
        const response = await teacherApi.getVideos(selectedClass.value)
        const videoData = response?.data || []
        contents.value = videoData.map(video => ({
          content_id: video.id,
          title: video.title,
          content_type: 'video',
          video_url: video.file_path,
          description: video.description,
          tags: '[]', // 视频标签需要单独处理
          is_published: true,
          created_at: video.upload_time
        }))
      } else {
        // 加载文章和资料内容
        const response = await teacherApi.getMaterials(selectedClass.value)
        const materialData = response?.data || []
        contents.value = materialData.map(material => ({
          content_id: material.id,
          title: material.title,
          content_type: 'article',
          body: material.description,
          attachments: `${material.title}|${material.file_path}`,
          is_published: true,
          created_at: material.upload_time
        }))
      }
      console.log('获取到的内容:', contents.value)
    } catch (error) {
      console.error('获取内容失败:', error)
      ElMessage.error('获取内容列表失败')
    }
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

const handleContentTypeChange = (type) => {
  // 切换内容类型时重置相关字段
  if (type !== 'video') {
    contentForm.value.video_url = ''
    contentForm.value.tags = []
    contentForm.value.description = ''
    fileList.value = []
  } else {
    contentForm.value.body = ''
    contentForm.value.attachments = ''
  }
}

// 处理标签切换
const handleTabChange = (tab) => {
  activeTab.value = tab
  // 重新加载内容
  loadContents()
}

// 视频上传前的验证
const beforeVideoUpload = (file) => {
  const isVideo = file.type.startsWith('video/')
  const isLt100M = file.size / 1024 / 1024 < 100

  if (!isVideo) {
    ElMessage.error('只能上传视频文件!')
    return false
  }
  if (!isLt100M) {
    ElMessage.error('视频大小不能超过100MB!')
    return false
  }
  uploadProgress.value = 0
  return true
}

// 文件上传前的验证
const beforeFileUpload = (file) => {
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB!')
    return false
  }
  return true
}

// 视频上传成功处理
const handleVideoUploadSuccess = (response) => {
  uploadProgress.value = 100
  if (response.success) {
    contentForm.value.video_url = response.video.file_path
    contentForm.value.title = contentForm.value.title || response.video.title
    contentForm.value.description = contentForm.value.description || response.video.description
    ElMessage.success('视频上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 文件上传成功处理
const handleFileUploadSuccess = (response, file) => {
  if (response.success) {
    // 构建附件信息
    const newAttachment = `${response.material.title || file.name}|${response.material.file_path}`
    if (contentForm.value.attachments) {
      contentForm.value.attachments += `,${newAttachment}`
    } else {
      contentForm.value.attachments = newAttachment
    }
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

// 处理上传错误
const handleUploadError = (error) => {
  uploadProgress.value = 0
  ElMessage.error('上传失败: ' + (error.message || '未知错误'))
}

// 处理文件移除
const handleFileRemove = (file) => {
  // 从attachments中移除对应的文件
  if (contentForm.value.attachments) {
    const attachments = contentForm.value.attachments.split(',')
    const updatedAttachments = attachments.filter(item => !item.startsWith(`${file.name}|`))
    contentForm.value.attachments = updatedAttachments.join(',')
  }
}

// 解析附件字符串为对象数组
const parseAttachments = (attachmentsStr) => {
  if (!attachmentsStr) return []
  return attachmentsStr.split(',').map(item => {
    const [name, url] = item.split('|')
    return { name, url }
  })
}

// 下载文件
const downloadFile = (url, filename) => {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const showTagInput = () => {
  inputVisible.value = true
  nextTick(() => {
    tagInputRef.value?.focus()
  })
}

const handleTagInputConfirm = () => {
  if (inputValue.value) {
    const tag = inputValue.value.trim()
    if (tag && !contentForm.value.tags.includes(tag)) {
      contentForm.value.tags.push(tag)
    }
  }
  inputVisible.value = false
  inputValue.value = ''
}

const removeTag = (tag) => {
  contentForm.value.tags = contentForm.value.tags.filter(t => t !== tag)
}

const showCreateDialog = () => {
  if (!selectedClass.value) {
    ElMessage.warning('请先选择班级')
    return
  }
  currentContentId.value = null
  isEditMode.value = false
  fileList.value = []
  uploadProgress.value = 0

  contentForm.value = {
    title: '',
    content_type: activeTab.value === 'video' ? 'video' : 'article',
    body: '',
    video_url: '',
    description: '',
    tags: [],
    is_published: false,
    class_id: selectedClass.value,
    attachments: ''
  }
  dialogVisible.value = true
}

const editContent = (content) => {
  currentContentId.value = content.content_id
  isEditMode.value = true

  // 处理标签数据（从JSON字符串转换为数组）
  let tags = []
  try {
    tags = JSON.parse(content.tags || '[]')
  } catch (e) {
    console.warn('解析标签失败:', e)
    tags = []
  }

  // 设置文件列表
  fileList.value = []
  if (content.attachments) {
    const attachments = parseAttachments(content.attachments)
    fileList.value = attachments.map(item => ({
      name: item.name,
      url: item.url,
      status: 'success'
    }))
  }

  contentForm.value = {
    ...content,
    tags: tags,
    class_id: selectedClass.value
  }

  // 如果是视频内容，确保切换到视频标签
  if (content.content_type === 'video' && activeTab.value !== 'video') {
    activeTab.value = 'video'
  } else if (content.content_type !== 'video' && activeTab.value === 'video') {
    activeTab.value = 'article'
  }

  dialogVisible.value = true
}

const submitContentForm = async () => {
  try {
    // 验证必填字段
    if (!contentForm.value.title) {
      ElMessage.warning('请输入标题')
      return
    }

    if (contentForm.value.content_type === 'video') {
      if (!contentForm.value.video_url) {
        ElMessage.warning('请上传视频文件')
        return
      }
      if (contentForm.value.tags.length === 0) {
        ElMessage.warning('请至少添加一个视频标签')
        return
      }
    }

    // 确保class_id正确设置
    contentForm.value.class_id = selectedClass.value

    // 根据内容类型调用不同的API
    if (contentForm.value.content_type === 'video') {
      // 视频内容处理
      const videoData = {
        title: contentForm.value.title,
        description: contentForm.value.description,
        tags: JSON.stringify(contentForm.value.tags)
      }

      if (currentContentId.value) {
        // 更新视频
        await teacherApi.updateVideo(currentContentId.value, videoData)
        ElMessage.success('视频更新成功')
      } else {
        // 视频已通过上传处理，这里只需更新信息
        if (!contentForm.value.video_url) {
          ElMessage.warning('请先上传视频文件')
          return
        }
      }
    } else {
      // 文章或资料内容处理
      const materialData = {
        title: contentForm.value.title,
        description: contentForm.value.body
      }

      if (currentContentId.value) {
        // 更新资料
        await teacherApi.updateMaterial(currentContentId.value, materialData)
        ElMessage.success('资料更新成功')
      } else {
        // 资料已通过上传处理，这里只需更新信息
        if (!contentForm.value.attachments) {
          ElMessage.warning('请先上传资料文件')
          return
        }
      }
    }

    dialogVisible.value = false

    // 重新加载内容列表
    await loadContents()

  } catch (error) {
    console.error('提交内容失败:', error)
    ElMessage.error(error.message || '操作失败')
  }
}

const deleteContent = async (contentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个内容吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 根据当前标签类型调用不同的删除API
    if (activeTab.value === 'video') {
      await teacherApi.deleteVideo(contentId)
    } else {
      await teacherApi.deleteMaterial(contentId)
    }

    ElMessage.success('内容删除成功')
    await loadContents()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.content-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-management ::v-deep(.el-card) {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.content-management ::v-deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.content-management ::v-deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
}

.content-management ::v-deep(.el-table th) {
  background: #f5f7fa;
  color: #333;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
}

.content-management ::v-deep(.el-table td) {
  background: #fff;
  color: #333;
  border-bottom: 1px solid #ebeef5;
}

.content-management ::v-deep(.el-table tr:hover td) {
  background: #f5f7fa;
}

.content-management ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.content-management ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.content-management ::v-deep(.el-button--primary) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
}

.content-management ::v-deep(.el-button--primary:hover) {
  background: rgba(102, 126, 234, 0.5);
  border-color: rgba(102, 126, 234, 0.7);
}

.content-management ::v-deep(.el-button--danger) {
  background: rgba(245, 108, 108, 0.2);
  border-color: rgba(245, 108, 108, 0.3);
  color: #f56c6c;
}

.content-management ::v-deep(.el-button--danger:hover) {
  background: rgba(245, 108, 108, 0.3);
  color: #fff;
}

.content-management ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.content-management ::v-deep(.el-dialog__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.content-management ::v-deep(.el-dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.content-management ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.content-management ::v-deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.8);
}

.content-management ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.content-management ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.content-management ::v-deep(.el-select) {
  width: 100%;
}

.content-management ::v-deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.content-management ::v-deep(.el-switch) {
  --el-switch-on-color: #667eea;
}

/* 标签样式 */
.content-management ::v-deep(.el-tag) {
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.content-management ::v-deep(.el-tag--small) {
  height: 24px;
  line-height: 22px;
  padding: 0 8px;
}
</style>
