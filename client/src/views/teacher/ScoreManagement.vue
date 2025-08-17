<template>
  <div class="score-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成绩管理</span>
          <el-select v-model="selectedClass" placeholder="选择班级" @change="loadScores">
            <el-option
              v-for="classItem in classes"
              :key="classItem.class_id"
              :label="classItem.name"
              :value="classItem.class_id"
            />
          </el-select>
        </div>
      </template>

      <el-table :data="scores" border style="width: 100%">
        <el-table-column prop="author.username" label="学生" />
        <el-table-column prop="title" label="报告标题" />
        <el-table-column prop="score" label="成绩">
          <template #default="scope">
            <el-tag :type="getScoreTag(scope.row.score)">
              {{ scope.row.score }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="feedback" label="反馈" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="editScore(scope.row)">修改</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 修改成绩对话框 -->
    <el-dialog v-model="scoreDialogVisible" title="修改成绩" width="50%">
      <el-form :model="scoreForm" label-width="100px">
        <el-form-item label="学生">
          <el-input v-model="scoreForm.studentName" disabled />
        </el-form-item>
        <el-form-item label="报告标题">
          <el-input v-model="scoreForm.reportTitle" disabled />
        </el-form-item>
        <el-form-item label="成绩" required>
          <el-input-number v-model="scoreForm.score" :min="0" :max="100" :step="0.5" />
        </el-form-item>
        <el-form-item label="反馈">
          <el-input v-model="scoreForm.feedback" type="textarea" :rows="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scoreDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitScore">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { ElMessage } from 'element-plus'

const teacherStore = useTeacherStore()

const classes = ref([])
const scores = ref([])
const selectedClass = ref(null)
const scoreDialogVisible = ref(false)
const scoreForm = ref({
  report_id: null,
  studentName: '',
  reportTitle: '',
  score: null,
  feedback: ''
})

onMounted(async () => {
  classes.value = await teacherStore.fetchClasses()
})

const loadScores = async () => {
  if (selectedClass.value) {
    scores.value = await teacherStore.fetchScores(selectedClass.value)
  }
}

const getScoreTag = (score) => {
  if (score >= 90) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

const editScore = (report) => {
  scoreForm.value = {
    report_id: report.report_id,
    studentName: report.author?.username || '',
    reportTitle: report.title,
    score: report.score || null,
    feedback: report.feedback || ''
  }
  scoreDialogVisible.value = true
}

const submitScore = async () => {
  try {
    if (scoreForm.value.score === null) {
      ElMessage.warning('请填写成绩')
      return
    }

    await teacherStore.updateScore(scoreForm.value.report_id, {
      score: scoreForm.value.score,
      feedback: scoreForm.value.feedback
    })
    ElMessage.success('成绩更新成功')
    scoreDialogVisible.value = false
    await loadScores()
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  }
}
</script>

<style scoped>
.score-management {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
