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
      <el-upload
        class="upload-demo"
        drag
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">请上传Excel文件，包含学号、姓名、邮箱等信息</div>
        </template>
      </el-upload>
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

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const importStudents = async () => {
  try {
    await teacherStore.importStudents(selectedClass.value, selectedFile.value)
    ElMessage.success('学生导入成功')
    importDialogVisible.value = false
    await loadStudents()
  } catch (error) {
    ElMessage.error(error.message || '导入失败')
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
</style>
