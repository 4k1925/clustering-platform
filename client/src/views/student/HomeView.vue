<template>
  <div class="home-view">
    <el-card class="intro-card">
      <template #header>
        <div class="card-header">
          <h2>聚类算法介绍</h2>
        </div>
      </template>

      <el-tabs v-model="activeAlgorithm">
        <el-tab-pane label="K-Means" name="kmeans">
          <h3>K-Means聚类算法</h3>
          <p>K-Means是最常用的聚类算法之一，通过迭代将数据划分为K个簇...</p>
          <div class="algorithm-image">
            <img src="@/assets/kmeans-demo.png" alt="K-Means示例">
          </div>
        </el-tab-pane>

        <el-tab-pane label="DBSCAN" name="dbscan">
          <h3>DBSCAN聚类算法</h3>
          <p>基于密度的空间聚类算法，能够发现任意形状的簇...</p>
        </el-tab-pane>

        <el-tab-pane label="层次聚类" name="hierarchical">
          <h3>层次聚类算法</h3>
          <p>通过构建树状结构进行聚类，分为凝聚式和分裂式两种...</p>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const activeAlgorithm = ref('kmeans')
</script>

<style scoped>
.home-view {
  padding: 20px;
}
.intro-card {
  max-width: 1000px;
  margin: 0 auto;
}
.algorithm-image {
  margin-top: 20px;
  text-align: center;
}
.algorithm-image img {
  max-width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
}
</style>
