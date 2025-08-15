import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: () => import('@/views/auth/ForgotPasswordView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/student',
      name: 'StudentHome',
      component: () => import('@/views/student/HomeView.vue'),
      meta: { requiresAuth: true, role: 'student' }
    },
    {
      path: '/teacher',
      name: 'TeacherHome',
      component: () => import('@/views/teacher/ClassManagement.vue'),
      meta: { requiresAuth: true, role: 'teacher' }
    },
    // 其他路由...
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 需要登录但未登录，重定向到登录页
    next('/login')
  } else if (to.meta.requiresAuth && to.meta.role && authStore.user.role !== to.meta.role) {
    // 角色不匹配，重定向到对应首页
    if (authStore.isTeacher) {
      next('/teacher')
    } else {
      next('/student')
    }
  } else {
    next()
  }
})

export default router
