<template>
  <div class="student-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生管理</span>
          <div>
            <el-select v-model="selectedClass" placeholder="选择班级" @change="loadStudents">
              <el-option
                v-for="classItem in classes"
                :key="classItem.class_id"
                :label="classItem.name"
                :value="classItem.class_id"
              />
            </el-select>
            <el-button type="primary" @click="showImportDialog" style="margin-left: 10px;">
              导入学生
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="students" border style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="student_id" label="学号" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" type="danger" @click="resetPassword(scope.row.user_id)">重置密码</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 导入学生对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入学生" width="30%">
      <!-- 移除 el-upload 组件，使用原生 input -->
      <div class="file-upload-area">
        <input
          type="file"
          ref="fileInput"
          accept=".xlsx,.xls"
          @change="handleFileChange"
          style="display: none"
        >
        <div
          class="upload-dropzone"
          @click="$refs.fileInput.click()"
          @drop="handleDrop"
          @dragover.prevent
          @dragenter.prevent
        >
          <el-icon class="upload-icon"><upload-filled /></el-icon>
          <div class="upload-text">拖拽文件到此处或<em>点击上传</em></div>
          <div class="upload-tip">请上传Excel文件(.xlsx, .xls, .csv), 包含学号、姓名、邮箱等信息</div>
          <div v-if="selectedFile" class="selected-file">
            已选择文件: {{ selectedFile.name }} ({{ formatFileSize(selectedFile.size) }})
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importStudents" :disabled="!selectedFile">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const teacherStore = useTeacherStore()
const fileInput = ref(null)
const classes = ref([])
const students = ref([])
const selectedClass = ref(null)
const importDialogVisible = ref(false)
const selectedFile = ref(null)


onMounted(async () => {
  classes.value = await teacherStore.fetchClasses()
})

const loadStudents = async () => {
  if (selectedClass.value) {
    students.value = await teacherStore.fetchStudents(selectedClass.value)
  }
}

const showImportDialog = () => {
  if (!selectedClass.value) {
    ElMessage.warning('请先选择班级')
    return
  }
  importDialogVisible.value = true
  selectedFile.value = null
}

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    console.log('选择的文件:', file)
    console.log('文件名:', file.name)
    console.log('文件类型:', file.type)

    // 简单的文件扩展名验证
    const fileName = file.name.toLowerCase()
    const isExcel = fileName.endsWith('.xlsx') || fileName.endsWith('.xls')
    const isCSV = fileName.endsWith('.csv')

    if (!isExcel && !isCSV) {
      ElMessage.error('请上传Excel文件 (.xlsx, .xls) 或 CSV文件 (.csv)')
      event.target.value = ''
      selectedFile.value = null
      return
    }

    selectedFile.value = file
    console.log('文件验证通过:', selectedFile.value)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    handleFileChange({ target: { files: [files[0]] } })
  }
}
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const importStudents = async () => {
  try {
    if (!selectedFile.value) {
      ElMessage.error('请先选择文件')
      return
    }

    console.log('选择的文件对象:', selectedFile.value)
    console.log('文件类型:', typeof selectedFile.value)
    console.log('是File实例:', selectedFile.value instanceof File)

    // 确保是有效的 File 对象
    if (!(selectedFile.value instanceof File)) {
      ElMessage.error('文件对象无效，请重新选择文件')
      return
    }

    await teacherStore.importStudents(selectedClass.value, selectedFile.value)
    ElMessage.success('学生导入成功')
    importDialogVisible.value = false
    selectedFile.value = null
    // 重置文件输入
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    await loadStudents()
  } catch (error) {
    console.error('完整错误:', error)

    if (error.response) {
      console.error('响应状态:', error.response.status)
      console.error('响应数据:', error.response.data)

      const errorMsg = error.response.data?.error || error.response.data?.message || '导入失败'
      ElMessage.error(`导入失败: ${errorMsg}`)
    } else if (error.request) {
      console.error('请求对象:', error.request)
      ElMessage.error('网络错误: 无法连接到服务器')
    } else {
      ElMessage.error(`导入失败: ${error.message}`)
    }
  }
}

const resetPassword = async (userId) => {
  try {
    await ElMessageBox.confirm('确定要重置该学生的密码吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await teacherStore.resetPassword(userId)
    ElMessage.success('密码已重置为默认密码')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
    }
  }
}
</script>

<style scoped>
.student-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.student-management ::v-deep(.el-card) {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 极光.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.student-management ::v-deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.student-management ::v-deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
}

.student-management ::v-deep(.el-table th) {
  background: #f5f7fa;
  color: #333;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
}

.student-management ::v-deep(.el-table td) {
  background: #fff;
  color: #333;
  border-bottom: 1px solid #ebeef5;
}

.student-management ::v-deep(.el-table tr:hover td) {
  background: #f5f7fa;
}

.student-management ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.student-management ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.student-management ::v-deep(.el-button--primary) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
}

.student-management ::v-deep(.el-button--primary:hover) {
  background: rgba(102, 126, 234, 0.5);
  border-color: rgba(102极光 126, 234, 0.7);
}

.student-management ::v-deep(.el-button--danger) {
  background: rgba(245, 108, 108, 0.2);
  border-color: rgba(245, 108, 108, 0.3);
  color: #f56c6c;
}

.student-management ::v-deep(.el-button--danger:hover) {
  background: rgba(245, 108, 108, 0.3);
  color: #fff;
}

.student-management ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.student-management ::v-deep(.el-dialog__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 极光px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.student-management ::v-deep(.el极光dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.student-management ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.8);
}

.student-management ::v-deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.8);
}

.student-management ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.student-management ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.file-upload-area {
  text-align: center;
}

.upload-dropzone {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 40px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-dropzone:hover {
  border-color: rgba(102, 126, 234, 0.5);
  background: rgba(102, 126, 234, 0.1);
}

.upload-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 16px;
}

.upload-text {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.upload-text em {
  color: #667eea;
  font-style: normal;
  font-weight: 500;
}

.upload-tip {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  margin-bottom: 16px;
}

.selected-file {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 16px;
}
</style>
