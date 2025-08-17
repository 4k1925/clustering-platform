<template>
  <div class="class-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="showCreateDialog">创建班级</el-button>
        </div>
      </template>

      <el-table :data="classes" border style="width: 100%">
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
  classes.value = await teacherStore.fetchClasses()
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
    if (currentClassId.value) {
      await teacherStore.updateClass(currentClassId.value, classForm.value)
      ElMessage.success('班级更新成功')
    } else {
      await teacherStore.createClass(classForm.value)
      ElMessage.success('班级创建成功')
    }
    dialogVisible.value = false
    await loadClasses()
  } catch (error) {
    ElMessage.error(error.message || '操作失败')
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
</style>
