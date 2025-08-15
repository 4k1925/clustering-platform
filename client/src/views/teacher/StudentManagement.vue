<template>
  <div class="student-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>学生信息管理</span>
          <div>
            <el-button type="primary" @click="showImportDialog">导入学生</el-button>
            <el-button @click="exportStudents">导出名单</el-button>
          </div>
        </div>
      </template>

      <el-table :data="students" border style="width: 100%">
        <el-table-column prop="studentId" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="className" label="班级" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="editStudent(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteStudent(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入学生信息" width="30%">
      <el-upload
        class="upload-demo"
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".xlsx,.csv"
      >
        <el-button type="primary">选择文件</el-button>
        <template #tip>
          <div class="el-upload__tip">请上传Excel或CSV格式的学生名单</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitImport">确认导入</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" :title="editDialogTitle">
      <el-form :model="currentStudent" label-width="80px">
        <el-form-item label="学号">
          <el-input v-model="currentStudent.studentId" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="currentStudent.name" />
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="currentStudent.classId" placeholder="选择班级">
            <el-option
              v-for="classItem in classes"
              :key="classItem.id"
              :label="classItem.name"
              :value="classItem.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="currentStudent.email" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveStudent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 模拟数据
const students = ref([
  { id: 1, studentId: '2023001', name: '张三', className: '计算机1班', email: 'zhangsan@example.com', classId: 1 },
  { id: 2, studentId: '2023002', name: '李四', className: '计算机2班', email: 'lisi@example.com', classId: 2 },
  { id: 3, studentId: '2023003', name: '王五', className: '计算机1班', email: 'wangwu@example.com', classId: 1 }
])

const classes = ref([
  { id: 1, name: '计算机1班' },
  { id: 2, name: '计算机2班' },
  { id: 3, name: '人工智能班' }
])

const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => students.value.length)
const importDialogVisible = ref(false)
const editDialogVisible = ref(false)
const currentStudent = ref({
  id: null,
  studentId: '',
  name: '',
  classId: null,
  email: ''
})

const editDialogTitle = computed(() => {
  return currentStudent.value.id ? '编辑学生信息' : '添加学生'
})

const showImportDialog = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file) => {
  console.log('文件已选择:', file)
  // 实际项目中这里应该处理文件内容
}

const submitImport = () => {
  ElMessage.success('导入成功(模拟)')
  importDialogVisible.value = false
}

const exportStudents = () => {
  ElMessage.success('导出成功(模拟)')
}

const editStudent = (student) => {
  currentStudent.value = { ...student }
  editDialogVisible.value = true
}

const deleteStudent = (student) => {
  students.value = students.value.filter(s => s.id !== student.id)
  ElMessage.success('删除成功')
}

const saveStudent = () => {
  if (currentStudent.value.id) {
    // 更新
    const index = students.value.findIndex(s => s.id === currentStudent.value.id)
    if (index !== -1) {
      students.value[index] = { ...currentStudent.value }
    }
  } else {
    // 新增
    currentStudent.value.id = students.value.length + 1
    students.value.push({ ...currentStudent.value })
  }
  ElMessage.success('保存成功')
  editDialogVisible.value = false
}

const handlePageChange = (page) => {
  currentPage.value = page
}

onMounted(() => {
  // 实际项目中这里应该调用API获取数据
})
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
.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
