<template>
  <div class="teacher-layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="logo">聚类算法教学平台</div>
      <div class="nav">
        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          @select="handleMenuSelect"
          background-color="transparent"
          text-color="rgba(255, 255, 255, 0.8)"
          active-text-color="#667eea"
        >
          <el-menu-item index="class">班级管理</el-menu-item>
          <el-menu-item index="student">学生管理</el-menu-item>
          <el-menu-item index="content">内容管理</el-menu-item>
          <el-menu-item index="report">报告批阅</el-menu-item>
          <el-menu-item index="score">成绩管理</el-menu-item>
        </el-menu>
      </div>
      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="40" :src="userInfo.avatar || defaultAvatar" />
            <span class="username">{{ userInfo.username }}</span>
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <div class="main-container">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ArrowDown } from '@element-plus/icons-vue'
import defaultAvatar from '@/assets/images/default-avatar.png'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const userInfo = computed(() => ({
  username: user.value?.username || '',
  avatar: user.value?.avatar || '',
  role: user.value?.role || ''
}))

// 当前激活的菜单项
const activeMenu = computed(() => {
  const path = route.path.split('/').pop()
  return path || 'class'
})

// 初始化用户信息
onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      authStore.logout()
    }
  }
})

const handleMenuSelect = (index) => {
  // 映射菜单index到实际路由
  const routeMap = {
    class: 'classes',
    student: 'students',
    content: 'contents',
    report: 'reports',
    score: 'scores'
  }
  router.push(`/teacher/${routeMap[index] || index}`)
}
const handleProfile = () => {
  router.push('/teacher/profile')
}

const handleLogout = async () => {
  try {
    // 添加确认对话框
    await ElMessageBox.confirm('确定要退出登录吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 调用authStore的logout方法
    authStore.logout()

    // 显示成功消息
    ElMessage.success('退出登录成功')

    // 跳转到登录页
    router.push('/login')

  } catch (error) {
    // 用户点击取消
    if (error === 'cancel') {
      ElMessage.info('已取消退出')
    } else {
      console.error('退出登录失败:', error)
      ElMessage.error('退出登录失败')
    }
  }
}
</script>

<style scoped>
.teacher-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  position: relative;
  overflow: hidden;
}

.teacher-layout::before {
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  color: white;
  padding: 0 20px;
  height: 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 30px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  flex: 1;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  display: flex;
  align-items: center;
  color: white;
  cursor: pointer;
}

.username {
  margin: 0 10px;
  font-weight: 500;
}

.main-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
  position: relative;
  z-index: 1;
}
</style>
