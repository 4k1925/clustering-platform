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
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
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
</script>

<style scoped>
.teacher-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f0f2f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #545c64;
  color: white;
  padding: 0 20px;
  height: 60px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  margin-right: 30px;
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
}

.main-container {
  flex: 1;
  padding: 20px;
  overflow: auto;
}
</style>
