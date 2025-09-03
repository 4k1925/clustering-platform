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
          <el-select v-model="contentForm.content_type" placeholder="请选择内容类型">
            <el-option label="视频" value="video" />
            <el-option label="文章" value="article" />
            <el-option label="代码示例" value="code_example" />
          </el-select>
        </el-form-item>
        <el-form-item label="视频URL" v-if="contentForm.content_type === 'video'">
          <el-input v-model="contentForm.video_url" placeholder="输入视频URL" />
          <div style="font-size: 12px; color: #666; margin-top: 5px;">
            支持格式：YouTube、Bilibili、腾讯视频等外链
          </div>
        </el-form-item>
        <el-form-item label="内容" v-if="contentForm.content_type !== 'video'">
          <el-input v-model="contentForm.body" type="textarea" :rows="10" placeholder="请输入详细内容..." />
        </el-form-item>
        <el-form-item label="附件" v-if="contentForm.content_type !== 'video'">
          <el-input v-model="contentForm.attachments" placeholder="附件信息（可选）" />
          <div style="font-size: 12px; color: #666; margin-top: 5px;">
            格式：文件名1|下载链接1,文件名2|下载链接2
          </div>
        </el-form-item>
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
import { ref, computed, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'

const teacherStore = useTeacherStore()

const classes = ref([])
const contents = ref([])
const selectedClass = ref(null)
const dialogVisible = ref(false)
const currentContentId = ref(null)
const contentForm = ref({
  title: '',
  content_type: 'article',
  body: '',
  video_url: '',
  is_published: false,
  class_id: null
})

const dialogTitle = computed(() => {
  return currentContentId.value ? '编辑内容' : '创建内容'
})
onMounted(async () => {
  try {
    classes.value = await teacherStore.fetchClasses()
    console.log('获取到的班级:', classes.value)

    // 确保contents数组已初始化
    if (!Array.isArray(teacherStore.contents)) {
      teacherStore.contents = []
    }
  } catch (error) {
    console.error('获取班级失败:', error)
    ElMessage.error('获取班级列表失败')
  }
})
// const loadContents = async () => {
//   if (selectedClass.value) {
//     contents.value = await teacherStore.fetchContents(selectedClass.value)
//   }
// }
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
    is_published: false,
    class_id: selectedClass.value
  }
  dialogVisible.value = true
}

const editContent = (content) => {
  currentContentId.value = content.content_id
  contentForm.value = {
    ...content,
    class_id: selectedClass.value // 确保class_id正确
  }
  dialogVisible.value = true
}

const submitContentForm = async () => {
  try {
    // 确保class_id正确设置
    contentForm.value.class_id = selectedClass.value

    if (currentContentId.value) {
      await teacherStore.updateContent(currentContentId.value, contentForm.value)
      ElMessage.success('内容更新成功')
    } else {
      await teacherStore.createContent(contentForm.value)
      ElMessage.success('内容创建成功')
    }
    dialogVisible.value = false

    // 无论创建还是更新，都重新加载内容列表确保数据一致
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
  border-color: rgba(245, 108, 极光, 0.3);
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
</style>
