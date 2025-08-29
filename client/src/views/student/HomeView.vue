<template>
  <div class="home-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>聚类算法介绍</h2>
        </div>
      </template>

      <el-tabs v-model="activeAlgorithm">
        <el-tab-pane label="K-Means" name="kmeans">
          <h3>K-Means 聚类算法</h3>
          <p>K-Means是最常用的聚类算法之一，它将数据划分为K个簇，每个簇由其质心表示。</p>

          <div class="algorithm-details">
            <h4>算法步骤:</h4>
            <ol>
              <li>随机选择K个初始质心</li>
              <li>将每个数据点分配到最近的质心</li>
              <li>重新计算每个簇的质心</li>
              <li>重复步骤2-3直到收敛</li>
            </ol>

            <h4>优点:</h4>
            <ul>
              <li>简单高效</li>
              <li>适用于大数据集</li>
              <li>结果易于解释</li>
            </ul>

            <h4>缺点:</h4>
            <ul>
              <li>需要预先指定K值</li>
              <li>对初始质心敏感</li>
              <li>只适用于凸形簇</li>
            </ul>
          </div>

          <div class="simulation-link">
            <el-button
              type="primary"
              @click="goToSimulation('kmeans')"
            >
              K-Means 算法模拟
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="DBSCAN" name="dbscan">
          <h3>DBSCAN 聚类算法</h3>
          <p>DBSCAN (Density-Based Spatial Clustering of Applications with Noise) 是一种基于密度的聚类算法。</p>

          <div class="algorithm-details">
            <h4>算法原理:</h4>
            <p>DBSCAN通过将紧密相连的点分组形成簇，能够发现任意形状的簇并识别噪声点。</p>

            <h4>核心概念:</h4>
            <ul>
              <li><strong>核心点:</strong> 邻域内至少有minPts个点的点</li>
              <li><strong>边界点:</strong> 在核心点的邻域内但自身不是核心点</li>
              <li><strong>噪声点:</strong> 既不是核心点也不是边界点的点</li>
            </ul>

            <h4>优点:</h4>
            <ul>
              <li>不需要预先指定簇的数量</li>
              <li>能够发现任意形状的簇</li>
              <li>对噪声有鲁棒性</li>
            </ul>
          </div>

          <div class="simulation-link">
            <el-button
              type="primary"
              @click="goToSimulation('dbscan')"
            >
              DBSCAN 算法模拟
            </el-button>
          </div>
        </el-tab-pane>

        <el-tab-pane label="层次聚类" name="hierarchical">
          <h3>层次聚类算法</h3>
          <p>层次聚类通过构建树状结构（树状图）来展示数据点之间的层次关系。</p>

          <div class="algorithm-details">
            <h4>算法类型:</h4>
            <ul>
              <li><strong>凝聚法 (Agglomerative):</strong> 自底向上，每个点开始都是单独的簇，然后逐渐合并</li>
              <li><strong>分裂法 (Divisive):</strong> 自顶向下，所有点开始都在一个簇中，然后逐渐分裂</li>
            </ul>

            <h4>距离度量:</h4>
            <ul>
              <li>单链接 (Single Linkage)</li>
              <li>全链接 (Complete Linkage)</li>
              <li>平均链接 (Average Linkage)</li>
              <li>质心链接 (Centroid Linkage)</li>
            </ul>

            <h4>优点:</h4>
            <ul>
              <li>不需要预先指定簇的数量</li>
              <li>结果的可视化（树状图）有助于理解数据结构</li>
            </ul>
          </div>

          <div class="simulation-link">
            <el-button
              type="primary"
              @click="goToSimulation('hierarchical')"
            >
              层次聚类算法模拟
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeAlgorithm = ref('kmeans')

const goToSimulation = (algorithm) => {
  router.push({
    name: 'AlgorithmSimulation',
    params: { algorithm }
  })
}
</script>

<style scoped>
.home-view {
  padding: 20px;
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
  min-height: 100vh;
}

.home-view ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.home-view ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
}

.card-header h2 {
  color: #fff;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.home-view ::v-deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.1);
}

.home-view ::v-deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  transition: all 0.3s ease;
}

.home-view ::v-deep(.el-tabs__item:hover) {
  color: #fff;
}

.home-view ::v-deep(.el-tabs__item.is-active) {
  color: #667eea;
}

.home-view ::v-deep(.el-tabs__active-bar) {
  background-color: #667eea;
}

.home-view ::v-deep(.el-tab-pane) {
  color: rgba(255, 255, 255, 0.9);
}

.home-view ::v-deep(.el-tab-pane h3) {
  color: #fff;
  font-size: 22px;
  margin-bottom: 20px;
  font-weight: 600;
}

.home-view ::v-deep(.el-tab-pane p) {
  line-height: 1.6;
  margin-bottom: 20px;
}

.algorithm-details {
  margin: 25px 0;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.algorithm-details h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #667eea;
  font-size: 18px;
  font-weight: 600;
}

.algorithm-details ol,
.algorithm-details ul {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  padding-left: 20px;
}

.algorithm-details li {
  margin-bottom: 8px;
}

.algorithm-details strong {
  color: #9b59b6;
}

.simulation-link {
  margin-top: 30px;
  text-align: center;
}

.home-view ::v-deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  border: none;
  border-radius: 12px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.home-view ::v-deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 
    0 10px 30px rgba(102, 126, 234, 0.4),
    0 0 20极光 rgba(155, 89, 182, 0.3);
}
</style>
