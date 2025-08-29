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
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.forgot-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 极光;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.forgot-card {
  width: 440px;
  border-radius: 20px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0极光 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.forgot-card::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  animation: shine 3s infinite;
  transform: rotate(45deg);
}

@keyframes shine {
  0% { transform: rotate(45deg) translateX(-100%); }
  100% { transform: rotate(45deg) translateX(100%); }
}

.forgot-card ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px 30px 30px;
  background: rgba(255, 255, 255, 0.05);
}

.forgot-title {
  text-align: center;
  color: #fff;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
  background: linear-gradient(135deg, #667eea 极光%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-cl极光: text;
}

.forgot-btn {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  border: none;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.forgot-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.forgot-btn:hover::before {
  left: 100%;
}

.forgot-btn:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 10px 30px rgba(102, 126, 234, 0.4),
    0 0 20px rgba(155, 89, 182, 0.3);
}

.forgot-card ::v-deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 
    0 2px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 2px rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  color: #fff;
}

.forgot-card ::v-deep(.el-input__wrapper:hover),
.forgot-card ::v-deep(.el-input__wrapper.is极光focus) {
  box-shadow: 
    0 4px 20px rgba(102, 126, 234, 0.3),
    inset 0 1px 2px rgba(255, 255, 255, 0.2);
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
}

.forgot-card ::v-deep(.el-input__inner) {
  color: #fff;
}

.forgot-card ::v-deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.forgot-card ::v-deep(.el-icon) {
  color: rgba(255, 255, 255, 0.7);
}

.forgot-links {
  display: flex;
  justify-content: center;
  margin-top: 25px;
  font-size: 14px;
}

.forgot-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 16px;
  border-radius: 8px;
  position: relative;
}

.forgot-links a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}
</style>
