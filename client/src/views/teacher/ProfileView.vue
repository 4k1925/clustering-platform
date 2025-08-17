<template>
  <div class="profile-view">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人中心</span>
        </div>
      </template>

      <div class="profile-content">
        <el-form label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="userInfo.username" disabled />
          </el-form-item>
          <el-form-item label="角色">
            <el-input v-model="userInfo.role" disabled />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="userInfo.email" />
          </el-form-item>
          <el-form-item label="头像">
            <el-upload
              class="avatar-uploader"
              action="/api/upload"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
            >
              <img v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="updateProfile">保存修改</el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <h3>修改密码</h3>
        <el-form label-width="100px">
          <el-form-item label="当前密码">
            <el-input v-model="password.old" type="password" />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="password.new" type="password" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="password.confirm" type="password" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="changePassword">修改密码</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()

const userInfo = ref({
  username: '',
  email: '',
  role: '',
  avatar: ''
})

const password = ref({
  old: '',
  new: '',
  confirm: ''
})

// 初始化用户信息
onMounted(() => {
  if (authStore.user) {
    userInfo.value = { ...authStore.user }
  }
})

// 头像上传成功
const handleAvatarSuccess = (response) => {
  userInfo.value.avatar = response.url
  ElMessage.success('头像上传成功')
}

// 更新个人信息
const updateProfile = async () => {
  try {
    // 调用API更新用户信息
    await authStore.updateProfile(userInfo.value)
    ElMessage.success('个人信息更新成功')
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  }
}

// 修改密码
const changePassword = async () => {
  if (password.value.new !== password.value.confirm) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  try {
    await authStore.changePassword({
      oldPassword: password.value.old,
      newPassword: password.value.new
    })
    ElMessage.success('密码修改成功')
    password.value = { old: '', new: '', confirm: '' }
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败')
  }
}
</script>

<style scoped>
.profile-view {
  padding: 20px;
}
.profile-card {
  max-width: 800px;
  margin: 0 auto;
}
.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100px;
  height: 100px;
}
.avatar-uploader:hover {
  border-color: #409eff;
}
.avatar {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}
</style>
