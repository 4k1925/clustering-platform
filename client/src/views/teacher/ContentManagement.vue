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
            <el-button type="primary" @click="showCreateDialog" style="margin-left: 10px;">
              创建内容
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="contents" border style="width: 100%">
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="content_type" label="类型">
          <template #default="scope">
            <el-tag :type="getContentTypeTag(scope.row.content_type)">
              {{ scope.row.content_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" v-if="selectedContentType === 'video'">
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
        <el-form-item label="内容类型" required>
          <el-select v-model="contentForm.content_type" placeholder="请选择内容类型" @change="handleContentTypeChange">
            <el-option label="视频" value="video" />
            <el-option label="文章" value="article" />
            <el-option label="代码示例" value="code_example" />
          </el-select>
        </el-form-item>
        
        <!-- 视频特定字段 -->
        <template v-if="contentForm.content_type === 'video'">
          <el-form-item label="视频URL" required>
            <el-input v-model="contentForm.video_url" placeholder="输入视频URL或上传路径" />
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
              支持格式：MP4、WebM等视频文件路径
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
          <el-form-item label="内容">
            <el-input v-model="contentForm.body" type="textarea" :rows="10" placeholder="请输入详细内容..." />
          </el-form-item>
          <el-form-item label="附件">
            <el-input v-model="contentForm.attachments" placeholder="附件信息（可选）" />
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
              格式：文件名1|下载链接1,文件名2|下载链接2
            </div>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'

const teacherStore = useTeacherStore()

const classes = ref([])
const contents = ref([])
const selectedClass = ref(null)
const dialogVisible = ref(false)
const currentContentId = ref(null)
const inputVisible = ref(false)
const inputValue = ref('')
const tagInputRef = ref(null)

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

const selectedContentType = computed(() => contentForm.value.content_type)

const dialogTitle = computed(() => {
  return currentContentId.value ? '编辑内容' : '创建内容'
})

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

const loadContents = async () => {
  if (selectedClass.value) {
    try {
      contents.value = await teacherStore.fetchContents(selectedClass.value)
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
  } else {
    contentForm.value.body = ''
    contentForm.value.attachments = ''
  }
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
  contentForm.value = {
    title: '',
    content_type: 'article',
    body: '',
    video_url: '',
    description: '',
    tags: [],
    is_published: false,
    class_id: selectedClass.value
  }
  dialogVisible.value = true
}

const editContent = (content) => {
  currentContentId.value = content.content_id
  
  // 处理标签数据（从JSON字符串转换为数组）
  let tags = []
  try {
    tags = JSON.parse(content.tags || '[]')
  } catch (e) {
    console.warn('解析标签失败:', e)
    tags = []
  }
  
  contentForm.value = {
    ...content,
    tags: tags,
    class_id: selectedClass.value
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
        ElMessage.warning('请输入视频URL')
        return
      }
      if (contentForm.value.tags.length === 0) {
        ElMessage.warning('请至少添加一个视频标签')
        return
      }
    }

    // 确保class_id正确设置
    contentForm.value.class_id = selectedClass.value

    // 准备提交数据（将标签数组转换为JSON字符串）
    const submitData = {
      ...contentForm.value,
      tags: JSON.stringify(contentForm.value.tags) // 转换为JSON字符串
    }

    if (currentContentId.value) {
      await teacherStore.updateContent(currentContentId.value, submitData)
      ElMessage.success('内容更新成功')
    } else {
      await teacherStore.createContent(submitData)
      ElMessage.success('内容创建成功')
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
    await teacherStore.deleteContent(contentId)
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