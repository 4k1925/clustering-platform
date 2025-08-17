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
 // 学生端路由
    {
      path: '/student',
      name: 'StudentLayout',
      component: () => import('@/views/student/StudentLayout.vue'),
      meta: { requiresAuth: true, role: 'student' },
      redirect: '/student/home',
      children: [
        {
          path: 'home',
          name: 'StudentHome',
          component: () => import('@/views/student/HomeView.vue'),
          meta: { title: '算法介绍' }
        },
        {
          path: 'videos',
          name: 'StudentVideos',
          component: () => import('@/views/student/VideoView.vue'),
          meta: { title: '教学视频' }
        },
        {
          path: 'code',
          name: 'StudentCode',
          component: () => import('@/views/student/CodeDebugView.vue'),
          meta: { title: '代码调试' }
        },
        {
          path: 'reports',
          name: 'StudentReports',
          component: () => import('@/views/student/ReportView.vue'),
          meta: { title: '实验报告' }
        },
        {
          path: 'scores',
          name: 'StudentScores',
          component: () => import('@/views/student/ScoreView.vue'),
          meta: { title: '我的成绩' }
        },
        {
          path: 'simulation/:algorithm?',
          name: 'AlgorithmSimulation',
          component: () => import('@/views/student/SimulationView.vue'),
          meta: { title: '算法模拟' },
          props: true
        }
      ]
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
      next('/student/home') // 修改为跳转到学生端首页
    }
  } else {
    next()
  }
})

export default router
