<template>
  <div class="report-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>实验报告管理</h2>
          <el-button type="primary" @click="showCreateDialog">
            新建报告
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="草稿箱" name="drafts">
          <el-table :data="draftReports" style="width: 100%">
            <el-table-column prop="title" label="报告标题" width="200" />
            <el-table-column prop="createdAt" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column prop="updatedAt" label="最后修改" width="180">
              <template #default="{ row }">
                {{ formatDate(row.updatedAt) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220">
              <template #default="{ row }">
                <el-button size="small" @click="editReport(row)">编辑</el-button>
                <el-button size="small" type="primary" @click="submitReport(row.id)">
                  提交
                </el-button>
                <el-button size="small" type="danger" @click="deleteReport(row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="已提交" name="submitted">
          <el-table :data="submittedReports" style="width: 100%">
            <el-table-column prop="title" label="报告标题" width="200" />
            <el-table-column prop="createdAt" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.createdAt) }}
              </template>
            </el-table-column>
            <el-table-column prop="submittedAt" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.submittedAt) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)">
                  {{ statusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="score" label="成绩" width="100">
              <template #default="{ row }">
                {{ row.score !== null ? row.score : '待批阅' }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" @click="viewReport(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 报告编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="isEditing ? '编辑报告' : '新建报告'"
      width="80%"
    >
      <el-form :model="currentReport" label-width="80px">
        <el-form-item label="报告标题" required>
          <el-input v-model="currentReport.title" />
        </el-form-item>

        <el-form-item label="报告内容" required>
          <MonacoEditor
            v-model="currentReport.content"
            language="markdown"
            :options="editorOptions"
            height="500px"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="saveReport">
          {{ isEditing ? '更新报告' : '创建报告' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MonacoEditor from '@/components/editor/MonacoEditor.vue'
import studentAPI from '@/api/student'
import { formatDate } from '@/utils/helpers'

const activeTab = ref('drafts')
const showDialog = ref(false)
const isEditing = ref(false)
const reports = ref([])
const currentReport = ref({
  id: null,
  title: '',
  content: ''
})

const editorOptions = {
  automaticLayout: true,
  minimap: { enabled: false }
}

const draftReports = computed(() =>
  reports.value.filter(r => r.status === 'draft')
)

const submittedReports = computed(() =>
  reports.value.filter(r => r.status === 'submitted' || r.status === 'reviewed')
)

const statusText = (status) => {
  const statusMap = {
    draft: '草稿',
    submitted: '已提交',
    reviewed: '已批阅'
  }
  return statusMap[status] || status
}

const statusTagType = (status) => {
  const typeMap = {
    draft: 'info',
    submitted: 'warning',
    reviewed: 'success'
  }
  return typeMap[status] || ''
}

const fetchReports = async () => {
  try {
    const response = await studentAPI.getReports()
    reports.value = response.data
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('获取报告列表失败')
  }
}

const showCreateDialog = () => {
  currentReport.value = { id: null, title: '', content: '' }
  isEditing.value = false
  showDialog.value = true
}

const editReport = (report) => {
  currentReport.value = { ...report }
  isEditing.value = true
  showDialog.value = true
}

const saveReport = async () => {
  if (!currentReport.value.title || !currentReport.value.content) {
    ElMessage.warning('请填写报告标题和内容')
    return
  }

  try {
    if (isEditing.value) {
      await studentAPI.updateReport(currentReport.value.id, currentReport.value)
      ElMessage.success('报告更新成功')
    } else {
      await studentAPI.createReport(currentReport.value)
      ElMessage.success('报告创建成功')
    }
    showDialog.value = false
    await fetchReports()
  } catch (error) {
    console.error('获取报告列表失败:', error)
    ElMessage.error('保存报告失败')
  }
}

const submitReport = async (reportId) => {
  try {
    await ElMessageBox.confirm('确定要提交该报告吗?提交后不能修改', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await studentAPI.submitReport(reportId)
    ElMessage.success('报告提交成功')
    await fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('获取报告列表失败:', error)
      ElMessage.error('提交报告失败')
    }
  }
}

const deleteReport = async (reportId) => {
  try {
    await ElMessageBox.confirm('确定要删除该报告吗?此操作不可恢复', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await studentAPI.deleteReport(reportId)
    ElMessage.success('报告删除成功')
    await fetchReports()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除报告失败')
    }
  }
}

const viewReport = (report) => {
  // 实际项目中应跳转到报告详情页
  ElMessage.info(`查看报告: ${report.title}`)
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.report-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
