<template>
  <div class="class-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="showCreateDialog">添加班级</el-button>
        </div>
      </template>

      <el-table :data="classes"  style="width: 100%">
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="course_code" label="课程代码" />
        <el-table-column prop="academic_year" label="学年" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editClass(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteClass(scope.row.class_id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑班级对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
      <el-form :model="classForm" label-width="100px">
        <el-form-item label="班级名称" required>
          <el-input v-model="classForm.name" />
        </el-form-item>
        <el-form-item label="课程代码" required>
          <el-input v-model="classForm.course_code" />
        </el-form-item>
        <el-form-item label="学年">
          <el-input v-model="classForm.academic_year" />
        </el-form-item>
        <el-form-item label="班级描述">
          <el-input v-model="classForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitClassForm">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage, ElMessageBox } from 'element-plus'

const teacherStore = useTeacherStore()
if (!teacherStore.classes) {
  teacherStore.classes = []
}
const classes = ref([])
const dialogVisible = ref(false)
const currentClassId = ref(null)
const classForm = ref({
  name: '',
  course_code: '',
  academic_year: '',
  description: ''
})

const dialogTitle = computed(() => {
  return currentClassId.value ? '编辑班级' : '创建班级'
})

onMounted(async () => {
  await loadClasses()
})

const loadClasses = async () => {
  try {
    console.log('开始加载班级...')
    // 直接使用返回值
    const classList = await teacherStore.fetchClasses()
    classes.value = classList
    console.log('班级加载成功:', classes.value)
  } catch (error) {
    console.error('加载班级失败:', error)
    ElMessage.error('加载班级列表失败')
    classes.value = []
  }
}

const showCreateDialog = () => {
  currentClassId.value = null
  classForm.value = {
    name: '',
    course_code: '',
    academic_year: '',
    description: ''
  }
  dialogVisible.value = true
}

const editClass = (classData) => {
  currentClassId.value = classData.class_id
  classForm.value = { ...classData }
  dialogVisible.value = true
}

const submitClassForm = async () => {
  try {
    const classData = {
      name: classForm.value.name.trim(),
      course_code: classForm.value.course_code.trim(),
      academic_year: classForm.value.academic_year?.trim() || '',
      description: classForm.value.description?.trim() || ''
    }

    if (!classData.name || !classData.course_code) {
      ElMessage.error('班级名称和课程代码为必填项')
      return
    }

    console.log('提交班级数据:', classData)

    // 等待创建完成
    await teacherStore.createClass(classData)
    ElMessage.success('班级创建成功')

    dialogVisible.value = false
    // 重新加载确保数据同步
    await loadClasses()

  } catch (error) {
    console.error('创建班级错误:', error)
    const errorMsg = error.response?.data?.error || error.message || '创建班级失败'
    ElMessage.error(errorMsg)
  }
}

const deleteClass = async (classId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个班级吗?', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await teacherStore.deleteClass(classId)
    ElMessage.success('班级删除成功')
    await loadClasses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.class-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-management ::v-deep(.el-card) {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.class-management ::v-deep(.el-card__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.class-management ::v-deep(.el-table) {
  background: transparent;
  border-radius: 8px;
  overflow: hidden;
}

.class-management ::v-deep(.el-table th) {
  background: #f5f7fa;
  color: #333;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
}

.class-management ::v-deep(.el-table td) {
  background: #fff;
  color: #333;
  border-bottom: 1px solid #ebeef5;
}

.class-management ::v-deep(.el-table tr:hover td) {
  background: #f5f7fa;
}

.class-management ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.class-management ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.class-management ::v-deep(.el-button--primary) {
  background: rgba(102, 126, 234, 0.3);
  border-color: rgba(102, 126, 234, 0.5);
  color: #fff;
}

.class-management ::v-deep(.el-button--primary:hover) {
  background: rgba(102, 126, 234, 0.5);
  border-color: rgba(102, 126, 234, 0.7);
}

.class-management ::v-deep(.el-button--danger) {
  background: rgba(245, 108, 108, 0.2);
  border-color: rgba(245, 108, 108, 0.3);
  color: #f56c6c;
}

.class-management ::v-deep(.el-button--danger:hover) {
  background: rgba(245, 108, 108, 0.3);
  color: #fff;
}

.class-management ::v-deep(.el-dialog) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.class-management ::v-deep(.el-dialog__header) {
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
}

.class-management ::v-deep(.el-dialog__title) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
}

.class-management ::v-deep(.el-dialog__body) {
  padding: 20px;
  color: rgba(255, 255, 255, 0.9);
}

.class-management ::v-deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.class-management ::v-deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.class-management ::v-deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}
</style>
