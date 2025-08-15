import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/student/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue')
  },
  // 学生路由
  {
    path: '/simulation',
    name: 'simulation',
    component: () => import('@/views/student/SimulationView.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/code-debug',
    name: 'code-debug',
    component: () => import('@/views/student/CodeDebugView.vue'),
    meta: { requiresAuth: true, role: 'student' }
  },
  // 教师路由
  {
    path: '/class-management',
    name: 'class-management',
    component: () => import('@/views/teacher/ClassManagement.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/report-review',
    name: 'report-review',
    component: () => import('@/views/teacher/ReportReview.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.role && authStore.user.role !== to.meta.role) {
    next('/') // 或者显示无权限页面
  } else {
    next()
  }
})

export default router
