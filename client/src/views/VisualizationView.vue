<template>
  <div class="home">
    <h1>{{ pageTitle }}</h1>
    <p>这里是聚类算法介绍页面</p>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      pageTitle: '聚类算法介绍'
    }
  },
}
</script>

<style scoped>
.home {
  padding: 20px;
}
h1 {
  color: #2c3e50;
}
</style>