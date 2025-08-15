<template>
  <div class="forgot-container">
    <el-card class="forgot-card">
      <template #header>
        <h2 class="forgot-title">重置密码</h2>
      </template>

      <el-form
        ref="forgotForm"
        :model="form"
        :rules="rules"
        @keyup.enter="handleSubmit"
      >
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="注册邮箱"
            prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="forgot-btn"
            :loading="loading"
            @click="handleSubmit"
          >
            发送重置链接
          </el-button>
        </el-form-item>

        <div class="forgot-links">
          <router-link to="/login">返回登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  email: ''
})

const rules = ref({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
})

const loading = ref(false)
const forgotForm = ref(null)

const handleSubmit = async () => {
  try {
    await forgotForm.value.validate()
    loading.value = true
    await authStore.requestPasswordReset(form.value.email)
    ElMessage.success('重置链接已发送到您的邮箱(模拟)')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '发送重置链接失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.forgot-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.forgot-title {
  text-align: center;
  color: #409EFF;
  margin: 0;
}

.forgot-btn {
  width: 100%;
}

.forgot-links {
  display: flex;
  justify-content: center;
  margin-top: 10px;
  font-size: 14px;
}

.forgot-links a {
  color: #606266;
  text-decoration: none;
}

.forgot-links a:hover {
  color: #409EFF;
}
</style>
