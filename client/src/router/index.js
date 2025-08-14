import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import VisualizationView from '../views/VisualizationView.vue'
import CodeEditorView from '../views/CodeEditorView.vue'
import ReportView from '../views/ReportView.vue'
import TestView from '../views/TestView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: '聚类算法介绍'
      }
    },
    {
      path: '/visualization',
      name: 'visualization',
      component: VisualizationView,
      meta: {
        title: '算法可视化'
      }
    },
    {
      path: '/code-editor',
      name: 'code-editor',
      component: CodeEditorView,
      meta: {
        title: '代码调试'
      }
    },
    {
      path: '/report',
      name: 'report',
      component: ReportView,
      meta: {
        title: '实验报告',
        requiresAuth: true
      }
    },
    {
      path: '/test',
      name: 'test',
      component: TestView,
      meta: {
        title: 'K-means测试页面'
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '聚类算法可视化学习平台'
  next()
})

export default router