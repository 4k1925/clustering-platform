<template>
  <div class="simulation-container">
    <el-card class="control-panel">
      <el-form label-width="100px">
        <el-form-item label="算法选择">
          <el-select v-model="algorithm" @change="resetSimulation">
            <el-option label="K-means" value="kmeans"></el-option>
            <el-option label="DBSCAN" value="dbscan"></el-option>
            <el-option label="层次聚类" value="hierarchical"></el-option>
          </el-select>
        </el-form-item>

        <el-button type="primary" @click="generateData">生成数据</el-button>
        <el-button type="success" @click="runClustering">运行聚类</el-button>
      </el-form>
    </el-card>

    <div class="visualization">
      <div ref="chartContainer" class="chart-container"></div>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as d3 from 'd3'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const chartContainer = ref(null)
const loading = ref(false)
const error = ref(null)

// 算法参数
const algorithm = ref('kmeans')
const simulationData = ref(null)

const resetSimulation = () => {
  simulationData.value = null
  d3.select(chartContainer.value).selectAll("*").remove()
}

const generateData = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await axios.get('/api/clustering/generate-data')
    simulationData.value = response.data
    renderData(simulationData.value.data)
    ElMessage.success('数据生成成功')
  } catch (err) {
    error.value = '数据生成失败: ' + err.message
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const runClustering = async () => {
  if (!simulationData.value) {
    ElMessage.warning('请先生成数据')
    return
  }

  try {
    loading.value = true
    error.value = null
    let endpoint = ''
    let params = {}

    switch (algorithm.value) {
      case 'kmeans':
        endpoint = '/api/clustering/kmeans'
        params = { n_clusters: 3 }
        break
      case 'dbscan':
        endpoint = '/api/clustering/dbscan'
        params = { eps: 0.5, min_samples: 5 }
        break
      case 'hierarchical':
        endpoint = '/api/clustering/hierarchical'
        params = { n_clusters: 3, linkage: 'ward' }
        break
    }

    const response = await axios.post(endpoint, {
      data: simulationData.value.data,
      ...params
    })

    renderClusters(simulationData.value.data, response.data.labels, response.data.centroids)
    ElMessage.success('聚类完成')
  } catch (err) {
    error.value = '聚类失败: ' + err.message
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

// 渲染原始数据
const renderData = (data) => {
  const margin = { top: 20, right: 20, bottom: 30, left: 40 }
  const width = 600 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  d3.select(chartContainer.value).selectAll("*").remove()

  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`)

  // 设置比例尺
  const x = d3.scaleLinear()
    .domain([d3.min(data, d => d[0]), d3.max(data, d => d[0])])
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([d3.min(data, d => d[1]), d3.max(data, d => d[1])])
    .range([height, 0])

  // 添加点
  svg.selectAll(".point")
    .data(data)
    .enter()
    .append("circle")
    .attr("class", "point")
    .attr("cx", d => x(d[0]))
    .attr("cy", d => y(d[1]))
    .attr("r", 5)
    .attr("fill", "#999")
}

// 渲染聚类结果
const renderClusters = (data, labels, centroids = null) => {
  const margin = { top: 20, right: 20, bottom: 30, left: 40 }
  const width = 600 - margin.left - margin.right
  const height = 400 - margin.top - margin.bottom

  d3.select(chartContainer.value).selectAll("*").remove()

  const svg = d3.select(chartContainer.value)
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`)

  // 设置比例尺
  const x = d3.scaleLinear()
    .domain([d3.min(data, d => d[0]), d3.max(data, d => d[0])])
    .range([0, width])

  const y = d3.scaleLinear()
    .domain([d3.min(data, d => d[1]), d3.max(data, d => d[1])])
    .range([height, 0])

  // 定义颜色比例尺
  const color = d3.scaleOrdinal()
    .domain([...new Set(labels)])
    .range(d3.schemeCategory10)

  // 添加点
  svg.selectAll(".point")
    .data(data)
    .enter()
    .append("circle")
    .attr("class", "point")
    .attr("cx", d => x(d[0]))
    .attr("cy", d => y(d[1]))
    .attr("r", 5)
    .attr("fill", (d, i) => color(labels[i]))

  // 添加质心（如果是K-means）
  if (centroids) {
    svg.selectAll(".centroid")
      .data(centroids)
      .enter()
      .append("circle")
      .attr("class", "centroid")
      .attr("cx", d => x(d[0]))
      .attr("cy", d => y(d[1]))
      .attr("r", 8)
      .attr("fill", (d, i) => color(i))
      .attr("stroke", "#000")
      .attr("stroke-width", 2)
  }
}

onMounted(() => {
  // 初始化时生成数据
  generateData()
})
</script>

<style scoped>
.simulation-container {
  display: flex;
  height: calc(100vh - 60px);
}

.control-panel {
  width: 300px;
  margin-right: 20px;
}

.visualization {
  flex: 1;
  position: relative;
}

.chart-container {
  width: 100%;
  height: 100%;
  border: 1px solid #eee;
}

.loading, .error {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 4px;
}

.error {
  color: red;
}
</style>
