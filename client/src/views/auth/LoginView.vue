<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">机器学习聚类算法平台</h2>
      </template>

      <el-form
        ref="loginForm"
        :model="form"
        :rules="rules"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-links">
          <router-link to="/register">注册账号</router-link>
          <router-link to="/forgot-password">忘记密码?</router-link>
        </div>
      </el-form>

      <div class="platform-features">
        <h4>平台功能特色</h4>
        <div class="features-list">
          <div>K-means聚类算法</div>
          <div>DBSCAN密度聚类</div>
          <div>层次聚类算法</div>
          <div>算法模拟实操</div>
          <div>实时算法调参</div>
          <div>聚类视频演示</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()


const form = ref({
  username: '',
  password: ''
})

const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
})

const loading = ref(false)
const loginForm = ref(null)

const handleLogin = async () => {
  try {
    await loginForm.value.validate()
    loading.value = true
    await authStore.loginUser(form.value)
    ElMessage.success('登录成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
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

.login-card {
  width: 440px;
  border-radius: 20px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.login-card::before {
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

.login-card ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px 30px 30px;
  background: rgba(255, 255, 255, 0.05);
}

.login-title {
  text-align: center;
  color: #fff;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-btn {
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

.login-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-btn:hover::before {
  left: 100%;
}

.login-btn:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 10px 30px rgba(102, 126, 234, 0.4),
    0 0 20px rgba(155, 89, 182, 0.3);
}

.login-card ::v-deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 
    0 2px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 2px rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
  color: #fff;
}

.login-card ::v-deep(.el-input__wrapper:hover),
.login-card ::v-deep(.el-input__wrapper.is-focus) {
  box-shadow: 
    0 4px 20px rgba(102, 126, 234, 0.3),
    inset 0 1px 2px rgba(255, 255, 255, 0.2);
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.12);
}

.login-card ::v-deep(.el-input__inner) {
  color: #fff;
}

.login-card ::v-deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.login-card ::v-deep(.el-icon) {
  color: rgba(255, 255, 255, 0.7);
}

.login-links {
  display: flex;
  justify-content: space-between;
  margin-top: 25px;
  font-size: 14px;
}

.login-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 16px;
  border-radius: 8px;
  position: relative;
}

.login-links a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  text-shadow: 0 0 10px rgba(255, 255, 255, 极光.3);
}

.platform-features {
  margin-top: 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.platform-features h4 {
  color: #fff;
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.features-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
}

.features-list div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.features-list div::before {
  content: '•';
  color: #667eea;
  font-weight: bold;
}
</style>
