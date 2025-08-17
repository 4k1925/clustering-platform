<template>
  <div class="simulation-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>{{ algorithmName }} 算法动态模拟</h2>
          <el-button @click="goBack">
            返回算法介绍
          </el-button>
        </div>
      </template>

      <div class="simulation-container">
        <div class="controls">
          <el-form label-width="120px">
            <el-form-item label="数据点数量">
              <el-slider v-model="pointCount" :min="10" :max="500" />
            </el-form-item>

            <el-form-item v-if="algorithm === 'kmeans'" label="簇数量 (K)">
              <el-slider v-model="kValue" :min="2" :max="10" />
            </el-form-item>

            <el-form-item v-if="algorithm === 'dbscan'" label="邻域半径 (ε)">
              <el-slider v-model="epsilon" :min="0.1" :max="2" :step="0.1" />
            </el-form-item>

            <el-form-item v-if="algorithm === 'dbscan'" label="最小点数">
              <el-slider v-model="minPoints" :min="1" :max="10" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="generateData">
                生成数据
              </el-button>
              <el-button @click="resetSimulation">
                重置
              </el-button>
            </el-form-item>
          </el-form>

          <div class="animation-controls" v-if="dataGenerated">
            <el-button @click="stepBackward" :disabled="!canStepBack">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button @click="toggleAnimation">
              {{ isAnimating ? '暂停' : '开始' }}
            </el-button>
            <el-button @click="stepForward" :disabled="!canStepForward">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <span>步骤: {{ currentStep + 1 }}/{{ simulationSteps.length }}</span>
          </div>
        </div>

        <div class="visualization">
          <div ref="canvasContainer" class="canvas-container"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as d3 from 'd3'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const algorithm = ref(route.params.algorithm || 'kmeans')
const canvasContainer = ref(null)

// 模拟参数
const pointCount = ref(100)
const kValue = ref(3)
const epsilon = ref(0.5)
const minPoints = ref(3)
const isAnimating = ref(false)
const animationInterval = ref(null)
const currentStep = ref(0)
const simulationSteps = ref([])
const dataGenerated = ref(false)
const svg = ref(null)

// 计算属性
const algorithmName = computed(() => {
  const names = {
    kmeans: 'K-Means',
    hierarchical: '层次聚类',
    dbscan: 'DBSCAN'
  }
  return names[algorithm.value] || '聚类'
})

const canStepBack = computed(() => currentStep.value > 0)
const canStepForward = computed(() => currentStep.value < simulationSteps.value.length - 1)

// 方法
const generateData = () => {
  // 生成随机数据点
  const data = Array.from({ length: pointCount.value }, () => ({
    x: Math.random() * 500,
    y: Math.random() * 500,
    cluster: null
  }))

  // 根据算法初始化模拟步骤
  if (algorithm.value === 'kmeans') {
    initializeKMeans(data)
  } else if (algorithm.value === 'dbscan') {
    initializeDBSCAN(data)
  } else {
    initializeHierarchical(data)
  }

  dataGenerated.value = true
  currentStep.value = 0
  renderSimulation()
}

const initializeKMeans = (data) => {
  // 1. 随机选择初始质心
  const centroids = []
  for (let i = 0; i < kValue.value; i++) {
    centroids.push({
      x: Math.random() * 500,
      y: Math.random() * 500,
      cluster: i
    })
  }

  simulationSteps.value = [{
    description: '随机选择初始质心',
    data: [...data],
    centroids: [...centroids]
  }]

  // 模拟K-Means步骤
  let changed = true
  let iteration = 0
  let currentCentroids = [...centroids]

  while (changed && iteration < 10) {
    changed = false

    // 分配步骤
    const newData = data.map(point => {
      let minDist = Infinity
      let cluster = -1

      currentCentroids.forEach((centroid, idx) => {
        const dist = Math.sqrt(
          Math.pow(point.x - centroid.x, 2) +
          Math.pow(point.y - centroid.y, 2)
        )

        if (dist < minDist) {
          minDist = dist
          cluster = idx
        }
      })

      return { ...point, cluster }
    })

    // 计算新质心
    const newCentroids = []
    for (let i = 0; i < kValue.value; i++) {
      const clusterPoints = newData.filter(p => p.cluster === i)
      if (clusterPoints.length > 0) {
        const sumX = clusterPoints.reduce((sum, p) => sum + p.x, 0)
        const sumY = clusterPoints.reduce((sum, p) => sum + p.y, 0)
        newCentroids.push({
          x: sumX / clusterPoints.length,
          y: sumY / clusterPoints.length,
          cluster: i
        })
      } else {
        // 如果某个簇没有点，保留原来的质心
        newCentroids.push(currentCentroids[i])
      }
    }

    // 检查质心是否变化
    for (let i = 0; i < kValue.value; i++) {
      const dx = newCentroids[i].x - currentCentroids[i].x
      const dy = newCentroids[i].y - currentCentroids[i].y
      if (Math.sqrt(dx * dx + dy * dy) > 0.1) {
        changed = true
        break
      }
    }

    // 保存当前步骤
    simulationSteps.value.push({
      description: `迭代 ${iteration + 1}: 分配点并更新质心`,
      data: [...newData],
      centroids: [...newCentroids]
    })

    currentCentroids = newCentroids
    iteration++
  }
}

const initializeDBSCAN = (data) => {
  // 简化的DBSCAN模拟
  simulationSteps.value = [
    { description: '初始数据点', data: [...data] },
    { description: '识别核心点', data: [...data] },
    { description: '形成簇', data: [...data] },
    { description: '标记噪声点', data: [...data] }
  ]
}

const initializeHierarchical = (data) => {
  // 简化的层次聚类模拟
  simulationSteps.value = [
    { description: '初始数据点', data: [...data] },
    { description: '计算距离矩阵', data: [...data] },
    { description: '合并最近簇', data: [...data] },
    { description: '更新距离矩阵', data: [...data] },
    { description: '形成层次结构', data: [...data] }
  ]
}

const renderSimulation = () => {
  if (!dataGenerated.value || !canvasContainer.value) return

  // 清除现有SVG
  d3.select(canvasContainer.value).selectAll('*').remove()

  // 创建SVG画布
  const width = canvasContainer.value.clientWidth
  const height = 500
  svg.value = d3.select(canvasContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // 获取当前步骤的数据
  const stepData = simulationSteps.value[currentStep.value]

  // 渲染数据点
  svg.value.selectAll('circle')
    .data(stepData.data)
    .enter()
    .append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', 5)
    .attr('fill', d => d.cluster !== null ? getClusterColor(d.cluster) : '#3498db')

  // 如果当前步骤有质心，渲染质心
  if (stepData.centroids) {
    svg.value.selectAll('rect.centroid')
      .data(stepData.centroids)
      .enter()
      .append('rect')
      .attr('x', d => d.x - 8)
      .attr('y', d => d.y - 8)
      .attr('width', 16)
      .attr('height', 16)
      .attr('fill', d => getClusterColor(d.cluster))
  }

  // 显示当前步骤描述
  svg.value.append('text')
    .attr('x', 10)
    .attr('y', 20)
    .attr('fill', '#333')
    .text(stepData.description)
}

const getClusterColor = (clusterIdx) => {
  const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
  return colors[clusterIdx % colors.length]
}

const stepForward = () => {
  if (canStepForward.value) {
    currentStep.value++
    renderSimulation()
  }
}

const stepBackward = () => {
  if (canStepBack.value) {
    currentStep.value--
    renderSimulation()
  }
}

const toggleAnimation = () => {
  if (isAnimating.value) {
    clearInterval(animationInterval.value)
    isAnimating.value = false
  } else {
    animationInterval.value = setInterval(() => {
      if (canStepForward.value) {
        currentStep.value++
        renderSimulation()
      } else {
        clearInterval(animationInterval.value)
        isAnimating.value = false
      }
    }, 1000)
    isAnimating.value = true
  }
}

const resetSimulation = () => {
  clearInterval(animationInterval.value)
  isAnimating.value = false
  dataGenerated.value = false
  currentStep.value = 0
  simulationSteps.value = []
  d3.select(canvasContainer.value).selectAll('*').remove()
}

const goBack = () => {
  router.push({ name: 'StudentHome' })
}

onMounted(() => {
  // 初始生成数据
  generateData()

  // 监听窗口大小变化
  window.addEventListener('resize', renderSimulation)
})

onUnmounted(() => {
  window.removeEventListener('resize', renderSimulation)
  clearInterval(animationInterval.value)
})
</script>

<style scoped>
.simulation-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.simulation-container {
  display: flex;
}

.controls {
  width: 300px;
  padding-right: 20px;
}

.visualization {
  flex: 1;
}

.canvas-container {
  width: 100%;
  height: 500px;
  border: 1px solid #eee;
  border-radius: 4px;
}

.animation-controls {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
