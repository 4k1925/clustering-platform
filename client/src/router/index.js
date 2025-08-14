import { createRouter, createWebHistory } from 'vue-router'
import StudentHome from '@/views/student/HomeView.vue'
import TeacherDashboard from '@/views/teacher/ClassManagement.vue'

const routes = [
  {
    path: '/student',
    component: () => import('@/layouts/StudentLayout.vue'),
    children: [
      { path: 'home', component: StudentHome },
    ]
  },
  {
    path: '/teacher',
    component: () => import('@/layouts/TeacherLayout.vue'),
    children: [
      { path: 'classes', component: TeacherDashboard },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
