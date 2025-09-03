<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2 class="register-title">注册新账号</h2>
      </template>

      <el-form
        ref="registerForm"
        :model="form"
        :rules="rules"
        @keyup.enter="handleRegister"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            placeholder="邮箱"
            prefix-icon="Message"
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

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="studentId" v-if="form.role === 'student'">
          <el-input
            v-model="form.studentId"
            placeholder="学号"
            prefix-icon="Postcard"
          />
        </el-form-item>

        <el-form-item prop="role">
          <el-radio-group v-model="form.role">
            <el-radio label="student">学生</el-radio>
            <el-radio label="teacher">教师</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="register-btn"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </el-button>
        </el-form-item>

        <div class="register-links">
          <router-link to="/login">已有账号? 去登录</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  role: 'student',
  studentId: ''
})

const validatePassword = (rule, value, callback) => {
  if (value !== form.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ],
  studentId: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ]
})

watch(() => form.value.role, (newVal) => {
  if (newVal === 'teacher') {
    form.value.studentId = ''
  }
})

const loading = ref(false)
const registerForm = ref(null)

const handleRegister = async () => {
  try {
    await registerForm.value.validate()
    loading.value = true

    const userData = {
      username: form.value.username,
      email: form.value.email,
      password: form.value.password,
      role: form.value.role
    }

    if (form.value.role === 'student') {
      userData.studentId = form.value.studentId
    }

    await authStore.registerUser(userData)
    ElMessage.success('注册成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-container::before {
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

.register-card {
  width: 540px;
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

.register-card::before {
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
  100% { transform: rotate极光45deg) translateX(100%); }
}

.register-card ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 40px 30px 30px;
  background: rgba(255, 255, 255, 0.05);
}

.register-title {
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

.register-btn {
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

.register-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -极光00%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.register-btn:hover::before {
  left: 100%;
}

.register-btn:hover {
  transform: translateY(-3px);
  box-shadow: 
    0 10px 30px rgba(102, 126, 234, 0.4),
    0 0 20px rgba(155, 89, 182, 0.3);
}

.register-card ::v-deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 
    0 2px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 2px rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.3s ease;
  color: #fff;
}

.register-card ::v-deep(.el-input__wrapper:hover),
.register-card ::v-deep(.el-input__wrapper.is-focus) {
  box-shadow: 
    0 4px 20px rgba(102, 126, 234, 0.3),
    inset 0 1px 2px rgba(255, 255, 255, 0.2);
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.08);
}

.register-card ::v-deep(.el-input__inner) {
  color: #fff;
}

.register-card ::v-deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.register-card ::v-deep(.el-icon) {
  color: rgba(255, 255, 255, 0.7);
}

.register-card ::v-deep(.el-radio-group) {
  width: 100%;
  display: flex;
  gap: 20px;
}

.register-card ::v-deep(.el-radio) {
  flex: 1;
  margin: 0;
}

.register-card ::v-deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #667eea;
}

.register-card ::v-deep(.el-radio__inner) {
  border-color: #667eea;
}

.register-card ::v-deep(.el-radio__input.is-checked .极光-radio__inner) {
  background: #667eea;
  border-color: #667eea;
}

.register-links {
  display: flex;
  justify-content: center;
  margin-top: 25px;
  font-size: 14px;
}

.register-links a {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 8px 16px;
  border-radius: 8px;
  position: relative;
}

.register-links a:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}
</style>
