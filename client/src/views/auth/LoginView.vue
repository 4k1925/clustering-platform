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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-title {
  text-align: center;
  color: #409EFF;
  margin: 0;
}

.login-btn {
  width: 100%;
}

.login-links {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
}

.login-links a {
  color: #606266;
  text-decoration: none;
}

.login-links a:hover {
  color: #409EFF;
}
</style>
