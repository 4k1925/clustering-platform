<template>
  <div class="test-view">
    <h1>K-means 算法测试页面</h1>
    <KMeansVisualization />
  </div>
</template>

<script>
// 导入KMeans可视化组件
import KMeansVisualization from '@/components/KMeansVisualization.vue'

export default {
  name: 'TestView',
  components: {
    KMeansVisualization
  }
}
</script>

<style scoped>
.test-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 30px;
}
</style>