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
              <el-slider v-model="pointCount" :min="10" :max="1000" show-input />
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
                <div class="method-description">
                  <p v-if="centroidMethod === 'random'">
                    <strong>随机选择：</strong>完全随机选择初始质心
                  </p>
                  <p v-if="centroidMethod === 'k-means++'">
                    <strong>K-Means++：</strong>智能选择相距较远的点作为质心
                  </p>
                  <p v-if="centroidMethod === 'custom'">
                    <strong>自定义：</strong>点击画布选择质心位置
                  </p>
                </div>
              </el-form-item>
<!-- 自定义质心控制 -->
              <el-form-item v-if="centroidMethod === 'custom'">
                <div class="custom-centroid-controls">
                  <el-button @click="startCustomCentroidSelection" type="primary">
                    {{ isSelectingCentroids ? '停止选择' : '开始选择质心' }}
                  </el-button>
                  <el-button @click="clearCustomCentroids" :disabled="customCentroids.length === 0">
                    清空已选
                  </el-button>
                  <div class="selected-count">
                    已选择: {{ customCentroids.length }}/{{ kValue }} 个质心
                  </div>
                  <div v-if="customCentroids.length > 0" class="centroid-preview">
                    <div v-for="(centroid, index) in customCentroids" :key="index" class="preview-item">
                      <span class="color-dot" :style="{ backgroundColor: getClusterColor(index) }"></span>
                      质心 {{ index + 1 }}: ({{ centroid.x.toFixed(2) }}, {{ centroid.y.toFixed(2) }})
                    </div>
                  </div>
                </div>
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

            <!-- GMM 特定参数 -->
            <template v-if="algorithm === 'gmm'">
              <el-form-item label="簇数量">
                <el-slider v-model="kValue" :min="2" :max="10" show-input />
              </el-form-item>
              <el-form-item label="协方差类型">
                <el-select v-model="covarianceType" placeholder="选择协方差类型">
                  <el-option label="Full" value="full" title="完全协方差矩阵，每个分量有自己的协方差矩阵" />
                  <el-option label="Tied" value="tied" title="所有分量共享同一个协方差矩阵" />
                  <el-option label="Diag" value="diag" title="对角协方差矩阵，每个分量有自己的对角协方差矩阵" />
                  <el-option label="Spherical" value="spherical" title="球面协方差矩阵，每个分量有自己的单一方差值" />
                </el-select>
              </el-form-item>
              <el-form-item label="最大迭代次数">
                <el-slider v-model="maxIterations" :min="10" :max="200" show-input />
              </el-form-item>
              <el-form-item label="收敛阈值">
                <el-slider v-model="tolerance" :min="0.0001" :max="0.01" :step="0.0001" show-input />
              </el-form-item>
            </template>

            <el-form-item>
              <el-button type="primary" @click="startSimulation" :loading="isLoading"
                :disabled="centroidMethod === 'custom' && customCentroids.length !== kValue">
                开始模拟
              </el-button>
              <el-button @click="resetSimulation">
                重置
              </el-button>
              <el-button @click="regenerateData" v-if="simulationData">
                重新生成数据
              </el-button>
            </el-form-item>
          </el-form>

          <!-- 性能指标 -->
          <div class="metrics" v-if="simulationData">
            <div class="metric-card">
              <div class="metric-label">迭代次数</div>
              <div class="metric-value">{{ simulationData.steps?.length - 1 || 0 }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">轮廓系数</div>
              <div class="metric-value">{{ metrics.silhouette || '0.00' }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">{{ algorithm === 'gmm' ? 'BIC' : 'SSE' }}</div>
              <div class="metric-value">{{ algorithm === 'gmm' ? (metrics.bic || '0.00') : (metrics.sse || '0.00') }}</div>
            </div>
            <!-- GMM 特定指标 -->
            <div class="metric-card" v-if="algorithm === 'gmm'">
              <div class="metric-label">AIC</div>
              <div class="metric-value">{{ metrics.aic || '0.00' }}</div>
            </div>
            <div class="metric-card" v-if="algorithm === 'gmm'">
              <div class="metric-label">收敛状态</div>
              <div class="metric-value">{{ metrics.converged !== undefined ? (metrics.converged ? '是' : '否') : '未知' }}</div>
            </div>
          </div>

          <!-- 动画控制 -->
          <div class="animation-controls" v-if="simulationData">
            <el-button @click="stepBackward" :disabled="!canStepBack">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button @click="toggleAnimation">
              {{ isAnimating ? '暂停' : '播放' }}
            </el-button>
            <el-button @click="stepForward" :disabled="!canStepForward">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <span>步骤: {{ currentStep + 1 }}/{{ simulationData.steps?.length || 0 }}</span>
            
            <div class="speed-control">
              <span>速度:</span>
              <el-slider v-model="animationSpeed" :min="100" :max="2000" :step="100" style="width: 100px" />
            </div>
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
    <div ref="canvasContainer" class="canvas-container" @click="handleCanvasClick">
      <!-- 选择模式指示器 -->
      <div v-if="isSelectingCentroids" class="selection-mode-indicator">
        <el-icon><Edit /></el-icon>
        点击选择质心位置 ({{ customCentroids.length }}/{{ kValue }})
      </div>
      
      <!-- 工具提示 -->
      <div class="tooltip" v-if="tooltip.visible" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
        <template v-if="tooltip.data.isCentroid">
          <div class="tooltip-header">质心 {{ tooltip.data.cluster + 1 }}</div>
          <div>位置: ({{ tooltip.data.x.toFixed(2) }}, {{ tooltip.data.y.toFixed(2) }})</div>
          <div v-if="tooltip.data.probability !== undefined">概率: {{ tooltip.data.probability.toFixed(3) }}</div>
        </template>
        <template v-else>
          <div>坐标: ({{ tooltip.data.x.toFixed(2) }}, {{ tooltip.data.y.toFixed(2) }})</div>
          <div>簇: {{ tooltip.data.cluster >= 0 ? `簇 ${tooltip.data.cluster + 1}` : '未分类' }}</div>
          <div v-if="tooltip.data.originalCluster !== undefined">
            原始簇: {{ tooltip.data.originalCluster >= 0 ? `簇 ${tooltip.data.originalCluster + 1}` : '无' }}
          </div>
          <div v-if="tooltip.data.probability !== undefined">
            概率: {{ tooltip.data.probability.toFixed(3) }}
          </div>
        </template>
      </div>
    </div>
    
    <div v-if="simulationData" class="step-description">
      <el-icon><InfoFilled /></el-icon>
      {{ currentStepDescription }}
      
      <!-- 添加性能指标显示 -->
      <div v-if="currentStep === simulationData.steps.length - 1 && simulationData.metrics" class="performance-metrics">
        <span class="metric-item" v-if="simulationData.metrics.silhouette">
          轮廓系数: {{ simulationData.metrics.silhouette }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.sse">
          SSE: {{ simulationData.metrics.sse }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.bic">
          BIC: {{ simulationData.metrics.bic }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.aic">
          AIC: {{ simulationData.metrics.aic }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.iterations">
          迭代: {{ simulationData.metrics.iterations }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.clusters">
          簇数: {{ simulationData.metrics.clusters }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.noise_points">
          噪声点: {{ simulationData.metrics.noise_points }}
        </span>
        <span class="metric-item" v-if="simulationData.metrics.converged !== undefined">
          收敛: {{ simulationData.metrics.converged ? '是' : '否' }}
        </span>
      </div>
  </div>
</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClusteringStore } from '@/stores/clustering'
import * as d3 from 'd3'
import { ArrowLeft, ArrowRight, InfoFilled, Edit } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus' // 添加ElMessage导入
// 添加自定义质心相关状态
// 添加自定义质心相关状态
const isSelectingCentroids = ref(false)
const customCentroids = ref([])
const route = useRoute()
const router = useRouter()
const clusteringStore = useClusteringStore()
const canvasContainer = ref(null)
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  data: {}
})

// 算法参数
const algorithm = ref(route.params.algorithm || 'kmeans')
const dataType = ref('gaussian')
const pointCount = ref(150)
const kValue = ref(3)
const centroidMethod = ref('random')
const epsilon = ref(0.5)
const minPoints = ref(5)
const nClusters = ref(3)
const linkageMethod = ref('ward')
const animationSpeed = ref(1000)
// 在算法参数部分增加
const covarianceType = ref('full')
const maxIterations = ref(100)
const tolerance = ref(0.001)
// 模拟状态
const isAnimating = ref(false)
const animationInterval = ref(null)
const isLoading = ref(false)
const error = ref(null)
const resizeObserver = ref(null)
const svg = ref(null)
const xScale = ref(null)
const yScale = ref(null)

// 从store获取数据
const simulationData = computed(() => clusteringStore.simulationData)
const currentStep = computed(() => clusteringStore.currentStep)
const dataTypes = computed(() => clusteringStore.dataTypes)
const centroidMethods = computed(() => clusteringStore.centroidMethods)

// 计算属性
const algorithmName = computed(() => {
  const names = {
    kmeans: 'K-Means',
    dbscan: 'DBSCAN',
    gmm: '高斯混合模型(GMM)'
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
  return steps[currentStep.value]?.description || '选择参数并开始模拟'
})

const metrics = computed(() => {
  if (!simulationData.value) return { silhouette: '0.00', sse: '0.00' }
  return simulationData.value.metrics || { silhouette: '0.00', sse: '0.00' }
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
      // 如果是自定义质心，添加自定义坐标
      if (centroidMethod.value === 'custom' && customCentroids.value.length > 0) {
        params.custom_centroids = customCentroids.value
      }
    } else if (algorithm.value === 'dbscan') {
      params.epsilon = epsilon.value
      params.min_points = minPoints.value
      // 验证参数有效性
  if (params.epsilon <= 0) {
    throw new Error('邻域半径 (ε) 必须大于0')
  }
  if (params.min_points < 1) {
    throw new Error('最小点数必须至少为1')
  }
    }else if (algorithm.value === 'gmm') {
  params.covariance_type = covarianceType.value
  params.max_iterations = maxIterations.value
  params.tolerance = tolerance.value
}

    await clusteringStore.simulateAlgorithm(algorithm.value, params)
    
    // 等待DOM更新后渲染
    await nextTick()
    initializeCanvas()
    renderSimulation()
    
  } catch (err) {
    error.value = err.message || '模拟失败'
    // 开发环境下使用模拟数据
    if (process.env.NODE_ENV === 'development') {
      useDemoData()
    }
  } finally {
    isLoading.value = false
    isSelectingCentroids.value = false // 停止选择模式
  }
}
// 自定义质心选择方法
const startCustomCentroidSelection = () => {
  isSelectingCentroids.value = !isSelectingCentroids.value
  if (!isSelectingCentroids.value) {
    // 如果停止选择但数量不够，提示用户
    if (customCentroids.value.length < kValue.value) {
      ElMessage.warning(`请选择至少 ${kValue.value} 个质心位置`)
    }
  }
}
const clearCustomCentroids = () => {
  customCentroids.value = []
  if (svg.value) {
    svg.value.selectAll('.temp-centroid').remove()
    svg.value.selectAll('.temp-centroid-label').remove()
  }
}
const handleCanvasClick = (event) => {
  if (!isSelectingCentroids.value || !xScale.value || !yScale.value) return
  if (customCentroids.value.length >= kValue.value) return

  // 获取点击位置的坐标（转换到数据坐标系）
  const rect = canvasContainer.value.getBoundingClientRect()
  const x = xScale.value.invert(event.clientX - rect.left)
  const y = yScale.value.invert(event.clientY - rect.top)
  
  // 限制在合理范围内
  const clampedX = Math.max(0, Math.min(10, x))
  const clampedY = Math.max(0, Math.min(10, y))
  
  // 添加自定义质心
  customCentroids.value.push({
    x: clampedX,
    y: clampedY
  })
  
  // 在画布上显示临时标记
  if (svg.value) {
    svg.value.selectAll('.temp-centroid').remove()
    
    customCentroids.value.forEach((centroid, index) => {
      svg.value.append('circle')
        .attr('class', 'temp-centroid')
        .attr('cx', xScale.value(centroid.x))
        .attr('cy', yScale.value(centroid.y))
        .attr('r', 8)
        .attr('fill', getClusterColor(index))
        .attr('stroke', '#000')
        .attr('stroke-width', 2)
        .attr('opacity', 0.8)
      
      svg.value.append('text')
        .attr('class', 'temp-centroid-label')
        .attr('x', xScale.value(centroid.x) + 12)
        .attr('y', yScale.value(centroid.y) - 12)
        .attr('fill', '#000')
        .attr('font-size', '12px')
        .attr('font-weight', 'bold')
        .text(`${index + 1}`)
    })
  }
  
  // 如果已选择足够数量的质心，自动停止选择
  if (customCentroids.value.length >= kValue.value) {
    isSelectingCentroids.value = false
  }
}

// 监听簇数量变化，重置自定义质心
watch(kValue, (newValue) => {
  if (customCentroids.value.length > newValue) {
    customCentroids.value = customCentroids.value.slice(0, newValue)
  }
})
const initializeCanvas = () => {
  if (!canvasContainer.value) return;
  
  // 清除现有内容
  d3.select(canvasContainer.value).selectAll('*').remove();
  
  const width = canvasContainer.value.clientWidth;
  const height = canvasContainer.value.clientHeight;
  
  // 创建SVG
  svg.value = d3.select(canvasContainer.value)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('class', 'simulation-svg');
  
  // 设置比例尺 - 增加边距，让画布更大
  const margin = { top: 20, right: 20, bottom: 40, left: 60 }; // 增加边距
  
  xScale.value = d3.scaleLinear()
    .domain([0, 10])
    .range([margin.left, width - margin.right]); // 使用边距
  
  yScale.value = d3.scaleLinear()
    .domain([0, 10])
    .range([height - margin.bottom, margin.top]); // 使用边距
  
  // 添加网格
  addGrid();
  

};



const renderSimulation = () => {
  if (!simulationData.value || !svg.value) return;

  const steps = simulationData.value.steps || [];
  if (steps.length === 0) return;

  const currentStepData = steps[currentStep.value];
  
  // 清除之前的可视化元素
  svg.value.selectAll('.data-point').remove();
  svg.value.selectAll('.centroid').remove();
  svg.value.selectAll('.centroid-line').remove();
  svg.value.selectAll('.info-text').remove();
  svg.value.selectAll('.grid').remove();
  svg.value.selectAll('.legend').remove(); // 确保清除图例

  // 添加网格背景
  addGrid();

  // 渲染数据点（固定位置）
  if (currentStepData.points && currentStepData.points.length > 0) {
    svg.value.selectAll('.data-point')
      .data(currentStepData.points)
      .enter()
      .append('circle')
      .attr('class', 'data-point')
      .attr('cx', d => xScale.value(d.x))
      .attr('cy', d => yScale.value(d.y))
      .attr('r', 4)
      .attr('fill', d => getClusterColor(d.cluster))
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .on('mouseover', function(event, d) {
        // 显示工具提示
        tooltip.value = {
          visible: true,
          x: event.pageX,
          y: event.pageY - 50,
          data: d
        };
        // 高亮点
        d3.select(this)
          .attr('r', 6)
          .attr('stroke-width', 2)
          .attr('stroke', '#000');
      })
      .on('mouseout', function() {
        // 隐藏工具提示
        tooltip.value.visible = false;
        // 恢复点样式
        d3.select(this)
          .attr('r', 4)
          .attr('stroke-width', 1.5)
          .attr('stroke', '#fff');
      });
      isSelectingCentroids.value = false
      customCentroids.value = []
  }

  // 渲染质心（只有K-Means有质心）
  if (algorithm.value === 'kmeans' && currentStepData.centroids && currentStepData.centroids.length > 0) {
    // 绘制质心移动轨迹（从上一个位置）
    if (currentStep.value > 0) {
      const prevStepData = steps[currentStep.value - 1];
      if (prevStepData.centroids) {
        currentStepData.centroids.forEach((centroid, idx) => {
          const prevCentroid = prevStepData.centroids[idx];
          if (prevCentroid && 
              (prevCentroid.x !== centroid.x || prevCentroid.y !== centroid.y)) {
            svg.value.append('line')
              .attr('class', 'centroid-line')
              .attr('x1', xScale.value(prevCentroid.x))
              .attr('y1', yScale.value(prevCentroid.y))
              .attr('x2', xScale.value(centroid.x))
              .attr('y2', yScale.value(centroid.y))
              .attr('stroke', getClusterColor(centroid.cluster))
              .attr('stroke-width', 2)
              .attr('stroke-dasharray', '4,4')
              .attr('opacity', 0.6);
          }
        });
      }
    }

    // 绘制质心
    svg.value.selectAll('.centroid')
      .data(currentStepData.centroids)
      .enter()
      .append('circle')
      .attr('class', 'centroid')
      .attr('cx', d => xScale.value(d.x))
      .attr('cy', d => yScale.value(d.y))
      .attr('r', 8)
      .attr('fill', d => getClusterColor(d.cluster))
      .attr('stroke', '#000')
      .attr('stroke-width', 2)
      .on('mouseover', function(event, d) {
        // 显示质心信息
        tooltip.value = {
          visible: true,
          x: event.pageX,
          y: event.pageY - 50,
          data: { ...d, isCentroid: true }
        };
        // 高亮质心
        d3.select(this)
          .attr('r', 10)
          .attr('stroke-width', 3);
      })
      .on('mouseout', function() {
        tooltip.value.visible = false;
        d3.select(this)
          .attr('r', 8)
          .attr('stroke-width', 2);
      });
  }

  // 显示步骤信息
  svg.value.append('text')
    .attr('class', 'info-text')
    .attr('x', 60)
    .attr('y', 30)
    .attr('fill', '#333')
    .attr('font-size', '16px')
    .attr('font-weight', 'bold')
    .text(`步骤 ${currentStep.value + 1}/${steps.length}: ${currentStepData.description}`)

  // 在最后一步显示性能指标
  if (currentStep.value === steps.length - 1 && simulationData.value.metrics) {
    const metrics = simulationData.value.metrics;
    let metricsText = `轮廓系数: ${metrics.silhouette}`;
    
    if (metrics.sse) metricsText += ` | SSE: ${metrics.sse}`;
    if (metrics.iterations) metricsText += ` | 迭代: ${metrics.iterations}`;
    if (metrics.clusters) metricsText += ` | 簇数: ${metrics.clusters}`;
    if (metrics.noise_points) metricsText += ` | 噪声点: ${metrics.noise_points}`;
    // 添加GMM特定指标
    if (metrics.bic) metricsText += ` | BIC: ${metrics.bic}`;
    if (metrics.aic) metricsText += ` | AIC: ${metrics.aic}`;
    if (metrics.converged !== undefined) metricsText += ` | 收敛: ${metrics.converged ? '是' : '否'}`;
    svg.value.append('text')
      .attr('class', 'info-text')
      .attr('x', 60)
      .attr('y', 55)
      .attr('fill', '#666')
      .attr('font-size', '14px')
      .text(metricsText);
  }
  // 添加图例
  addLegend(currentStepData);
};

// 添加网格背景
const addGrid = () => {
  // 水平网格线
  svg.value.append('g')
    .attr('class', 'grid')
    .selectAll('line')
    .data(yScale.value.ticks(10))
    .enter()
    .append('line')
    .attr('x1', xScale.value(0))
    .attr('x2', xScale.value(10))
    .attr('y1', d => yScale.value(d))
    .attr('y2', d => yScale.value(d))
    .attr('stroke', '#e0e0e0')
    .attr('stroke-width', 1);

  // 垂直网格线
  svg.value.append('g')
    .attr('class', 'grid')
    .selectAll('line')
    .data(xScale.value.ticks(10))
    .enter()
    .append('line')
    .attr('x1', d => xScale.value(d))
    .attr('x2', d => xScale.value(d))
    .attr('y1', yScale.value(0))
    .attr('y2', yScale.value(10))
    .attr('stroke', '#e0e0e0')
    .attr('stroke-width', 1);
};

// 添加图例
// 添加图例
const addLegend = (currentStepData) => {
  // 先清除之前的图例
  svg.value.selectAll('.legend').remove();
  
  const points = currentStepData.points || [];
  const clusters = [...new Set(points.map(p => p.cluster))].filter(c => c >= 0);
  
  if (clusters.length === 0) return;

  // 对簇序号进行排序和重新映射
  const sortedClusters = [...clusters].sort((a, b) => a - b);
  const clusterMap = new Map();
  sortedClusters.forEach((clusterId, index) => {
    clusterMap.set(clusterId, index); // 映射到连续的序号
  });

  const legend = svg.value.append('g')
    .attr('class', 'legend')
    .attr('transform', `translate(${xScale.value(9)}, ${yScale.value(9)})`);

  sortedClusters.forEach((clusterId, index) => {
    const displayIndex = clusterMap.get(clusterId); // 获取显示序号
    
    const legendItem = legend.append('g')
      .attr('transform', `translate(0, ${index * 25})`);

    legendItem.append('circle')
      .attr('r', 6)
      .attr('fill', getClusterColor(clusterId)) // 使用原始clusterId获取颜色
      .attr('stroke', '#000')
      .attr('stroke-width', 1);

    legendItem.append('text')
      .attr('x', 15)
      .attr('y', 4)
      .attr('fill', '#333')
      .attr('font-size', '12px')
      .text(`簇 ${displayIndex + 1}`); // 显示连续的序号
  });

  // 如果有噪声点（cluster = -1）
  if (points.some(p => p.cluster === -1)) {
    const noiseItem = legend.append('g')
      .attr('transform', `translate(0, ${sortedClusters.length * 25})`);
    
    noiseItem.append('circle')
      .attr('r', 6)
      .attr('fill', getClusterColor(-1))
      .attr('stroke', '#000')
      .attr('stroke-width', 1)
      .attr('opacity', 0.7);

    noiseItem.append('text')
      .attr('x', 15)
      .attr('y', 4)
      .attr('fill', '#333')
      .attr('font-size', '12px')
      .text('噪声点');
  }
};

// 获取簇颜色
const getClusterColor = (clusterIdx) => {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', 
    '#8A4FFF', '#00C853', '#FF4081', '#3F51B5',
    '#FF9800', '#9C27B0', '#2196F3', '#4CAF50'
  ];
  return clusterIdx !== null && clusterIdx !== undefined && clusterIdx >= 0 
    ? colors[clusterIdx % colors.length] 
    : '#95a5a6'; // 灰色表示噪声点或未分类点
};

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
    }, 2100 - animationSpeed.value)
    isAnimating.value = true
  }
}

const resetSimulation = () => {
  clearInterval(animationInterval.value)
  isAnimating.value = false
  clusteringStore.reset()
  if (canvasContainer.value) {
    d3.select(canvasContainer.value).selectAll('*').remove()
  }
  tooltip.value.visible = false
  initializeCanvas()
}

const regenerateData = () => {
  resetSimulation();
  setTimeout(() => {
    startSimulation();
  }, 100);
};

const goBack = () => {
  router.push({ name: 'StudentHome' })
}

// 演示数据（用于开发测试）
const useDemoData = () => {
  if (algorithm.value === 'dbscan') {
    // DBSCAN演示数据
    clusteringStore.simulationData = {
      algorithm: "dbscan",
      metrics: {
        silhouette: 0.68,
        clusters: 3,
        noise_points: 12,
        iterations: 1
      },
      status: "success",
      steps: [
        {
          description: "初始数据点",
          points: generateDBSCANPoints(150)
        },
        {
          description: "识别核心点",
          points: generateDBSCANPoints(150, 0.3)
        },
        {
          description: "形成簇结构",
          points: generateDBSCANPoints(150, 0.6)
        },
        {
          description: "标记噪声点",
          points: generateDBSCANPoints(150, 0.9)
        },
        {
          description: "DBSCAN聚类完成",
          points: generateDBSCANPoints(150, 1.0)
        }
      ]
    }
  } else if (algorithm.value === 'kmeans') {
  clusteringStore.simulationData = {
    algorithm: "kmeans",
    metrics: {
      silhouette: 0.72,
      sse: 245.36,
      iterations: 5
    },
    status: "success",
    steps: [
      {
        centroids: [
          { cluster: 0, x: 2.5, y: 7.5 },
          { cluster: 1, x: 7.5, y: 2.5 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ],
        description: "随机选择初始质心",
        points: generateDemoPoints(150)
      },
      {
        centroids: [
          { cluster: 0, x: 2.8, y: 7.2 },
          { cluster: 1, x: 7.2, y: 2.8 },
          { cluster: 2, x: 5.2, y: 5.3 }
        ],
        description: "迭代 1: 分配点到最近质心",
        points: generateDemoPoints(150, 0.3)
      },
      {
        centroids: [
          { cluster: 0, x: 3.0, y: 7.0 },
          { cluster: 1, x: 7.0, y: 3.0 },
          { cluster: 2, x: 5.1, y: 5.1 }
        ],
        description: "迭代 2: 更新质心位置",
        points: generateDemoPoints(150, 0.6)
      },
      {
        centroids: [
          { cluster: 0, x: 3.1, y: 6.9 },
          { cluster: 1, x: 6.9, y: 3.1 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ],
        description: "迭代 3: 重新分配点",
        points: generateDemoPoints(150, 0.8)
      },
      {
        centroids: [
          { cluster: 0, x: 3.2, y: 6.8 },
          { cluster: 1, x: 6.8, y: 3.2 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ],
        description: "迭代 4: 质心收敛",
        points: generateDemoPoints(150, 0.95)
      },
      {
        centroids: [
          { cluster: 0, x: 3.2, y: 6.8 },
          { cluster: 1, x: 6.8, y: 3.2 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ],
        description: "收敛完成 - 算法结束",
        points: generateDemoPoints(150, 1.0)
      }
    ]
  }
 
}else if (algorithm.value === 'gmm') {
  // GMM演示数据
  clusteringStore.simulationData = {
    algorithm: "gmm",
    metrics: {
      silhouette: 0.75,
      bic: -1200.45,
      aic: -1150.32,
      iterations: 25,
      converged: true
    },
    status: "success",
    steps: [
      {
        description: "初始化高斯分布",
        points: generateGMMPoints(150, 0.1),
        centroids: [
          { cluster: 0, x: 2.5, y: 7.5 },
          { cluster: 1, x: 7.5, y: 2.5 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ]
      },
      {
        description: "EM算法 - E步骤: 计算响应度",
        points: generateGMMPoints(150, 0.3),
        centroids: [
          { cluster: 0, x: 2.8, y: 7.2 },
          { cluster: 1, x: 7.2, y: 2.8 },
          { cluster: 2, x: 5.2, y: 5.3 }
        ]
      },
      {
        description: "EM算法 - M步骤: 更新参数",
        points: generateGMMPoints(150, 0.5),
        centroids: [
          { cluster: 0, x: 3.0, y: 7.0 },
          { cluster: 1, x: 7.0, y: 3.0 },
          { cluster: 2, x: 5.1, y: 5.1 }
        ]
      },
      {
        description: "迭代优化中",
        points: generateGMMPoints(150, 0.7),
        centroids: [
          { cluster: 0, x: 3.1, y: 6.9 },
          { cluster: 1, x: 6.9, y: 3.1 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ]
      },
      {
        description: "收敛完成 - 算法结束",
        points: generateGMMPoints(150, 1.0),
        centroids: [
          { cluster: 0, x: 3.2, y: 6.8 },
          { cluster: 1, x: 6.8, y: 3.2 },
          { cluster: 2, x: 5.0, y: 5.0 }
        ]
      }
    ]
  }
}
 clusteringStore.currentStep = 0
  initializeCanvas()
  renderSimulation()
}

// 添加GMM数据点生成函数
const generateGMMPoints = (count, convergence = 0) => {
  const points = []
  const clusters = 3
  
  for (let i = 0; i < count; i++) {
    let x, y, cluster
    
    if (i < count / 3) {
      // 簇1 - 左上角
      x = 2.5 + (Math.random() - 0.5) * (2 - convergence * 1.5)
      y = 7.5 + (Math.random() - 0.5) * (2 - convergence * 1.5)
      cluster = 0
    } else if (i < (2 * count) / 3) {
      // 簇2 - 右下角
      x = 7.5 + (Math.random() - 0.5) * (2 - convergence * 1.5)
      y = 2.5 + (Math.random() - 0.5) * (2 - convergence * 1.5)
      cluster = 1
    } else {
      // 簇3 - 中间
      x = 5.0 + (Math.random() - 0.5) * (3 - convergence * 2)
      y = 5.0 + (Math.random() - 0.5) * (3 - convergence * 2)
      cluster = 2
    }
    
    // 添加一些随机性
    x += (Math.random() - 0.5) * 0.5
    y += (Math.random() - 0.5) * 0.5
    
    points.push({ x, y, cluster })
  }
  return points
}
// 添加生成DBSCAN数据的方法：
const generateDBSCANPoints = (count, convergence = 0) => {
  const points = []
  const clusters = 3
  const noiseRatio = 0.08 // 噪声点比例
  
  for (let i = 0; i < count; i++) {
    let x, y, cluster
    
    if (i < count * (1 - noiseRatio)) {
      // 正常数据点（属于某个簇）
      const clusterIdx = i % clusters
      
      if (clusterIdx === 0) {
        // 簇1 - 左上角
        x = 2 + Math.random() * 2 + convergence * 0.5
        y = 7 + Math.random() * 2 - convergence * 0.5
        cluster = 0
      } else if (clusterIdx === 1) {
        // 簇2 - 右下角
        x = 6 + Math.random() * 2 - convergence * 0.5
        y = 2 + Math.random() * 2 + convergence * 0.5
        cluster = 1
      } else {
        // 簇3 - 中间
        x = 4 + Math.random() * 2
        y = 4 + Math.random() * 2
        cluster = 2
      }
    } else {
      // 噪声点
      x = Math.random() * 10
      y = Math.random() * 10
      cluster = -1 // -1 表示噪声点
    }
    
    // 添加一些随机性
    x += (Math.random() - 0.5) * 0.5
    y += (Math.random() - 0.5) * 0.5
    
    points.push({ x, y, cluster, originalCluster: cluster })
  }
  return points
}
const generateDemoPoints = (count, convergence = 0) => {
  const points = []
  for (let i = 0; i < count; i++) {
    let x, y, cluster
    
    if (i < count / 3) {
      // 簇1
      x = 2.5 + (Math.random() - 0.5) * 2 + convergence * 0.7
      y = 7.5 + (Math.random() - 0.5) * 2 - convergence * 0.7
      cluster = 0
    } else if (i < (2 * count) / 3) {
      // 簇2
      x = 7.5 + (Math.random() - 0.5) * 2 - convergence * 0.7
      y = 2.5 + (Math.random() - 0.5) * 2 + convergence * 0.7
      cluster = 1
    } else {
      // 簇3
      x = 5.0 + (Math.random() - 0.5) * 3
      y = 5.0 + (Math.random() - 0.5) * 3
      cluster = 2
    }
    
    points.push({ x, y, cluster })
  }
  return points
}

// 初始化
onMounted(() => {
  initializeCanvas()
  
  onUnmounted(() => {
    if (resizeObserver.value) {
      resizeObserver.value.disconnect()
    }
    clearInterval(animationInterval.value)
  })
  
  // 设置 resize observer
  resizeObserver.value = new ResizeObserver(() => {
    if (simulationData.value) {
      initializeCanvas()
      renderSimulation()
    }
  })
  
  if (canvasContainer.value) {
    resizeObserver.value.observe(canvasContainer.value)
  }
  
  // 加载配置数据
  clusteringStore.fetchDataTypes()
  clusteringStore.fetchCentroidMethods()
  
  // 开发环境下预加载演示数据
  if (process.env.NODE_ENV === 'development') {
    useDemoData()
  }
})

// 监听当前步骤变化
watch(currentStep, renderSimulation)

// 监听模拟数据变化

// 监听参数变化 - 修复监听器
watch([
  () => dataType.value,
  () => pointCount.value,
  () => kValue.value,
  () => centroidMethod.value,
  () => epsilon.value,
  () => minPoints.value,
  () => nClusters.value, // 现在这个变量已定义
  () => linkageMethod.value
], () => {
  if (simulationData.value) {
    resetSimulation();
  }
});
// 在已有的watch之后添加：
// 监听质心方法变化
watch(centroidMethod, (newMethod) => {
  if (newMethod !== 'custom') {
    isSelectingCentroids.value = false
    customCentroids.value = []
    if (svg.value) {
      svg.value.selectAll('.temp-centroid').remove()
      svg.value.selectAll('.temp-centroid-label').remove()
    }
  }
})
</script>

<style scoped>
/* 在style部分添加 */
.noise-point {
  stroke-dasharray: 2,2;
}
.custom-centroid-controls {
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px dashed #409eff;
}

.selected-count {
  margin: 8px 0;
  font-size: 14px;
  color: #409eff;
  font-weight: bold;
}

.centroid-preview {
  margin-top: 8px;
  padding: 8px;
  background: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.preview-item {
  display: flex;
  align-items: center;
  margin: 4px 0;
  font-size: 12px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  border: 1px solid #000;
}

.selection-mode-indicator {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 16px;
  border-radius: 20px;
  border: 2px solid #409eff;
  color: #409eff;
  font-weight: bold;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 8px;
}

.method-description {
  margin-top: 8px;
  padding: 8px;
  background: #f0f9ff;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.method-description p {
  margin: 4px 0;
  font-size: 12px;
  color: #606266;
}

.method-description strong {
  color: #409eff;
}
.simulation-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 调整控制面板和可视化区域的比例 */
.simulation-container {
  display: flex;
  gap: 20px;
  min-height: 700px; /* 增加整体高度 */
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
  height: 600px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  position: relative;
  overflow: hidden;
}

.step-description {
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 6px;
  font-weight: bold;
  color: #303133;
  border-left: 4px solid #409eff;
}

.animation-controls {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.animation-controls span {
  margin-left: 10px;
  font-size: 14px;
  color: #606266;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 20px;
}

.metric-card {
  background: #fff;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  margin: 8px 0;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.tooltip {
  position: absolute;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.85);
  color: white;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.tooltip div {
  margin: 2px 0;
}
</style>