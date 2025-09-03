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

        <el-tab-pane label="高斯混合模型(GMM)" name="gmm">
        <h3>高斯混合模型(GMM)算法</h3>
        <p>高斯混合模型是一种基于概率模型的聚类算法，假设数据由多个高斯分布混合生成，通过EM算法进行参数估计。</p>

        <div class="algorithm-details">
          <h4>核心概念:</h4>
          <ul>
            <li><strong>概率模型:</strong> 每个数据点属于各个簇的概率，而不是硬分配</li>
            <li><strong>EM算法:</strong> 通过期望最大化(Expectation-Maximization)算法迭代优化参数</li>
            <li><strong>软聚类:</strong> 提供每个点属于各个簇的概率分布</li>
          </ul>

          <h4>关键参数:</h4>
          <ul>
            <li><strong>分量数量:</strong> 高斯分布的数量（即簇的数量）</li>
            <li><strong>协方差类型:</strong>
              <ul>
                <li>Full - 完全协方差矩阵</li>
                <li>Tied - 所有分量共享同一协方差矩阵</li>
                <li>Diag - 对角协方差矩阵</li>
                <li>Spherical - 球面协方差矩阵</li>
              </ul>
            </li>
            <li><strong>收敛阈值:</strong> 似然函数变化的停止条件</li>
          </ul>

          <h4>优点:</h4>
          <ul>
            <li>提供软聚类结果，包含概率信息</li>
            <li>能够处理不同形状和大小的簇</li>
            <li>有坚实的统计学理论基础</li>
            <li>可以用于密度估计和新颖点检测</li>
          </ul>

          <h4>应用场景:</h4>
          <ul>
            <li>图像分割和计算机视觉</li>
            <li>语音识别和音频处理</li>
            <li>生物信息学和基因表达分析</li>
            <li>任何需要概率输出的聚类任务</li>
          </ul>

          <h4>数学模型:</h4>
          <p>GMM的概率密度函数为：</p>
          <p class="formula">p(x) = Σ<sub>k=1</sub><sup>K</sup> π<sub>k</sub> N(x | μ<sub>k</sub>, Σ<sub>k</sub>)</p>
          <p>其中：</p>
          <ul>
            <li>π<sub>k</sub> - 第k个高斯分布的混合系数</li>
            <li>μ<sub>k</sub> - 第k个高斯分布的均值向量</li>
            <li>Σ<sub>k</sub> - 第k个高斯分布的协方差矩阵</li>
            <li>N(x | μ, Σ) - 多元高斯分布</li>
          </ul>
        </div>

        <div class="simulation-link">
          <el-button
            type="primary"
            @click="goToSimulation('gmm')"
          >
            GMM算法动态模拟
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
