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
            <!-- 数据类型选择 -->
            <el-form-item label="数据类型">
              <el-select v-model="dataType" placeholder="选择数据类型">
                <el-option
                  v-for="type in dataTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
                  :title="type.description"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="数据点数量">
              <el-slider v-model="pointCount" :min="10" :max="500" show-input />
            </el-form-item>

            <!-- K-Means 特定参数 -->
            <template v-if="algorithm === 'kmeans'">
              <el-form-item label="簇数量 (K)">
                <el-slider v-model="kValue" :min="2" :max="10" show-input />
              </el-form-item>
              <el-form-item label="质心选择方法">
                <el-select v-model="centroidMethod" placeholder="选择质心方法">
                  <el-option
                    v-for="method in centroidMethods"
                    :key="method.value"
                    :label="method.label"
                    :value="method.value"
                    :title="method.description"
                  />
                </el-select>
              </el-form-item>
            </template>

            <!-- DBSCAN 特定参数 -->
            <template v-if="algorithm === 'dbscan'">
              <el-form-item label="邻域半径 (ε)">
                <el-slider v-model="epsilon" :min="0.1" :max="2" :step="0.1" show-input />
              </el-form-item>
              <el-form-item label="最小点数">
                <el-slider v-model="minPoints" :min="1" :max="10" show-input />
              </el-form-item>
            </template>

            <!-- 层次聚类特定参数 -->
            <template v-if="algorithm === 'hierarchical'">
              <el-form-item label="簇数量">
                <el-slider v-model="nClusters" :min="2" :max="10" show-input />
              </el-form-item>
              <el-form-item label="连接方法">
                <el-select v-model="linkageMethod" placeholder="选择连接方法">
                  <el-option label="Ward" value="ward" />
                  <el-option label="Complete" value="complete" />
                  <el-option label="Average" value="average" />
                  <el-option label="Single" value="single" />
                </el-select>
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="startSimulation" :loading="isLoading">
                开始模拟
              </el-button>
              <el-button @click="resetSimulation">
                重置
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 动画控制 -->
          <div class="animation-controls" v-if="simulationData">
            <el-button @click="stepBackward" :disabled="!canStepBack">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button @click="toggleAnimation">
              {{ isAnimating ? '暂停' : '开始' }}
            </el-button>
            <el-button @click="stepForward" :disabled="!canStepForward">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <span>步骤: {{ currentStep + 1 }}/{{ simulationData.steps?.length || 0 }}</span>
          </div>

          <!-- 错误显示 -->
          <el-alert
            v-if="error"
            :title="error"
            type="error"
            show-icon
            closable
            @close="error = null"
            style="margin-top: 20px"
          />
        </div>

        <div class="visualization">
          <div ref="canvasContainer" class="canvas-container"></div>
          <div v-if="simulationData" class="step-description">
            {{ currentStepDescription }}
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClusteringStore } from '@/stores/clustering'
import * as d3 from 'd3'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const clusteringStore = useClusteringStore()
const canvasContainer = ref(null)

// 算法参数
const algorithm = ref(route.params.algorithm || 'kmeans')
const dataType = ref('uniform')
const pointCount = ref(100)
const kValue = ref(3)
const centroidMethod = ref('random')
const epsilon = ref(0.5)
const minPoints = ref(5)
const nClusters = ref(3)
const linkageMethod = ref('ward')

// 模拟状态
const isAnimating = ref(false)
const animationInterval = ref(null)
const isLoading = ref(false)
const error = ref(null)

// 从store获取数据
const simulationData = computed(() => clusteringStore.simulationData)
const currentStep = computed(() => clusteringStore.currentStep)
const dataTypes = computed(() => clusteringStore.dataTypes)
const centroidMethods = computed(() => clusteringStore.centroidMethods)

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
const canStepForward = computed(() => {
  const steps = simulationData.value?.steps || []
  return currentStep.value < steps.length - 1
})

const currentStepDescription = computed(() => {
  const steps = simulationData.value?.steps || []
  return steps[currentStep.value]?.description || ''
})

// 方法
const startSimulation = async () => {
  try {
    isLoading.value = true
    error.value = null

    const params = {
      data_type: dataType.value,
      point_count: pointCount.value
    }

    if (algorithm.value === 'kmeans') {
      params.k_value = kValue.value
      params.centroid_method = centroidMethod.value
    } else if (algorithm.value === 'dbscan') {
      params.epsilon = epsilon.value
      params.min_points = minPoints.value
    } else if (algorithm.value === 'hierarchical') {
      params.n_clusters = nClusters.value
      params.linkage = linkageMethod.value
    }

    await clusteringStore.simulateAlgorithm(algorithm.value, params)
    renderSimulation()
  } catch (err) {
    error.value = err.message || '模拟失败'
  } finally {
    isLoading.value = false
  }
}

const renderSimulation = () => {
  if (!simulationData.value || !canvasContainer.value) return

  const steps = simulationData.value.steps || []
  if (steps.length === 0) return

  const currentStepData = steps[currentStep.value]

  // 清除现有SVG
  d3.select(canvasContainer.value).selectAll('*').remove()

  // 创建SVG画布
  const width = canvasContainer.value.clientWidth
  const height = 500
  const svg = d3.select(canvasContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)

  // 渲染数据点
  svg.selectAll('circle')
    .data(currentStepData.points || [])
    .enter()
    .append('circle')
    .attr('cx', d => d.x)
    .attr('cy', d => d.y)
    .attr('r', 5)
    .attr('fill', d => getClusterColor(d.cluster))

  // 渲染质心（如果有）
  if (currentStepData.centroids) {
    svg.selectAll('rect.centroid')
      .data(currentStepData.centroids)
      .enter()
      .append('rect')
      .attr('x', d => d.x - 8)
      .attr('y', d => d.y - 8)
      .attr('width', 16)
      .attr('height', 16)
      .attr('fill', d => getClusterColor(d.cluster))
      .attr('stroke', '#000')
      .attr('stroke-width', 2)
  }

  // 显示当前步骤描述
  svg.append('text')
    .attr('x', 10)
    .attr('y', 20)
    .attr('fill', '#333')
    .attr('font-size', '14px')
    .attr('font-weight', 'bold')
    .text(currentStepData.description)
}

const getClusterColor = (clusterIdx) => {
  const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22', '#27ae60']
  return clusterIdx !== null && clusterIdx !== undefined && clusterIdx >= 0
    ? colors[clusterIdx % colors.length]
    : '#95a5a6' // 灰色表示未分类点
}

const stepForward = () => {
  if (canStepForward.value) {
    clusteringStore.currentStep++
    renderSimulation()
  }
}

const stepBackward = () => {
  if (canStepBack.value) {
    clusteringStore.currentStep--
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
        stepForward()
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
  clusteringStore.reset()
  d3.select(canvasContainer.value).selectAll('*').remove()
}

const goBack = () => {
  router.push({ name: 'StudentHome' })
}

// 初始化
onMounted(async () => {
  await clusteringStore.fetchDataTypes()
  await clusteringStore.fetchCentroidMethods()

  // 监听窗口大小变化
  window.addEventListener('resize', renderSimulation)
})

onUnmounted(() => {
  window.removeEventListener('resize', renderSimulation)
  clearInterval(animationInterval.value)
  clusteringStore.reset()
})

// 监听当前步骤变化
watch(currentStep, renderSimulation)
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
  gap: 20px;
}

.controls {
  width: 350px;
  min-width: 350px;
}

.visualization {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.canvas-container {
  width: 100%;
  height: 500px;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #f8f9fa;
}

.step-description {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-weight: bold;
  color: #606266;
}

.animation-controls {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.animation-controls span {
  margin-left: 10px;
  font-size: 14px;
  color: #606266;
}
</style>
