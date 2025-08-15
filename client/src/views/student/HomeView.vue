<template>
  <div class="home-view">
    <h1>聚类算法介绍</h1>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="K-Means" name="kmeans">
        <kmeans-intro />
      </el-tab-pane>
      <el-tab-pane label="DBSCAN" name="dbscan">
        <dbscan-intro />
      </el-tab-pane>
      <el-tab-pane label="层次聚类" name="hierarchical">
        <hierarchical-intro />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import KmeansIntro from '@/components/clustering/KmeansIntro.vue'
import DbscanIntro from '@/components/clustering/DbscanIntro.vue'
import HierarchicalIntro from '@/components/clustering/HierarchicalIntro.vue'

const activeTab = ref('kmeans')
</script>
