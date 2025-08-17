<template>
  <div class="student-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">机器学习聚类平台</div>
        <div class="user-info">
          <el-dropdown>
            <span class="el-dropdown-link">
              {{ authStore.user.username }}
              <el-icon class="el-icon--right">
                <arrow-down />
              </el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px">
          <el-menu
            router
            :default-active="$route.path"
            class="student-menu"
          >
            <el-menu-item index="/student/home">
              <el-icon><House /></el-icon>
              <span>算法介绍</span>
            </el-menu-item>
            <el-menu-item index="/student/videos">
              <el-icon><VideoCamera /></el-icon>
              <span>教学视频</span>
            </el-menu-item>
            <el-menu-item index="/student/code">
              <el-icon><Cpu /></el-icon>
              <span>代码调试</span>
            </el-menu-item>
            <el-menu-item index="/student/reports">
              <el-icon><Document /></el-icon>
              <span>实验报告</span>
            </el-menu-item>
            <el-menu-item index="/student/scores">
              <el-icon><Trophy /></el-icon>
              <span>我的成绩</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import {
  House,
  VideoCamera,
  Cpu,
  Document,
  Trophy,
  ArrowDown
} from '@element-plus/icons-vue'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.student-layout {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #2c3e50;
  color: white;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.user-info {
  color: white;
}

.student-menu {
  height: calc(100vh - 60px);
}
</style>
