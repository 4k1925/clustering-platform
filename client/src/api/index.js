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
          path: 'simulation/:algorithm',
          name: 'AlgorithmSimulation',
          component: () => import('@/views/student/SimulationView.vue'),
          meta: { title: '算法模拟' }
        },
        {
          path: 'videos',
          name: 'StudentVideos',
          component: () => import('@/views/student/VideoView.vue'),
          meta: { title: '教学视频' }
        },
        // 在student路由中添加视频详情页
        {
          path: 'video/:id',
          name: 'VideoDetail',
          component: () => import('@/views/student/VideoDetailView.vue'),
          meta: { requiresAuth: true, role: 'student' }
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
          path: 'contents',
          name: 'StudentContents',
          component: () => import('@/views/student/CourseContentView.vue'),
          meta: { title: '课程资料' }
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
    // 教师端路由
    {
      path: '/teacher',
      name: 'TeacherLayout',
      component: () => import('@/views/teacher/TeacherLayout.vue'),
      meta: { requiresAuth: true, role: 'teacher' },
      redirect: '/teacher/classes',
      children: [
        {
          path: 'classes',
          name: 'ClassManagement',
          component: () => import('@/views/teacher/ClassManagement.vue'),
          meta: { title: '班级管理' }
        },
        {
          path: 'students',
          name: 'StudentManagement',
          component: () => import('@/views/teacher/StudentManagement.vue'),
          meta: { title: '学生管理' }
        },
        {
          path: 'contents',
          name: 'ContentManagement',
          component: () => import('@/views/teacher/ContentManagement.vue'),
          meta: { title: '内容管理' }
        },
        {
          path: 'reports',
          name: 'ReportReview',
          component: () => import('@/views/teacher/ReportReview.vue'),
          meta: { title: '报告批阅' }
        },
        {
          path: 'scores',
          name: 'ScoreManagement',
          component: () => import('@/views/teacher/ScoreManagement.vue'),
          meta: { title: '成绩管理' }
        },
         {
          path: 'profile',
          name: 'TeacherProfile',
          component: () => import('@/views/teacher/ProfileView.vue'),
          meta: { title: '个人中心' }
        }
      ]
    },

    // 404页面
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 如果目标路由需要认证但用户未登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  // 如果用户已登录但角色不匹配
  if (to.meta.requiresAuth && to.meta.role && authStore.user?.role !== to.meta.role) {
    // 根据用户角色重定向到对应首页
    if (authStore.user?.role === 'teacher') {
      next('/teacher/classes')
    } else {
      next('/student/home')
    }
    return
  }

  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 聚类算法教学平台`
  }

  next()
})

export default router
