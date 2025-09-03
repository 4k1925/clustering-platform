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
            <el-menu-item index="/student/contents">
              <el-icon><Notebook /></el-icon>
              <span>课程资料</span>
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
  Notebook,
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
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 极光, 0.1);
  padding: 0 30px;
  height: 70px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-cl极光: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.user-info {
  color: rgba(255, 255, 255, 0.9);
}

.user-info ::v-deep(.el-dropdown-link) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.3s ease;
}

.user-info ::v-deep(.el-dropdown-link:hover) {
  color: #fff;
}

.user-info ::v-deep(.el-icon) {
  color: rgba(255, 255, 255, 0.7);
}

.user-info ::v-deep(.el-dropdown-menu) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.user-info ::v-deep(.el-dropdown-menu__item) {
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.user-info ::v-deep(.el-dropdown-menu__item:hover) {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
}

.el-aside {
  background: rgba(255, 255, 255, 0.05);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  min-height: calc(100vh - 70px);
}

.student-menu {
  height: 100%;
  background: transparent;
  border-right: none;
}

.student-menu ::v-deep(.el-menu) {
  background: transparent;
  border-right: none;
}

.student-menu ::v-deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.7);
  height: 56px;
  line-height: 56px;
  margin: 4px 12px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.student-menu ::v-deep(.el-menu-item:hover) {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
}

.student-menu ::v-deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  color: #fff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.student-menu ::v-deep(.el-icon) {
  color: inherit;
  font-size: 18px;
}

.el-main {
  background: transparent;
  padding: 20px;
  overflow-x: hidden;
  min-height: calc(100vh - 70px);
}

.el-container {
  min-height: 100vh;
}
</style>
