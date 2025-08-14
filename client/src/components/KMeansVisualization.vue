<template>
  <div class="kmeans-container">
    <div ref="chartContainer" class="kmeans-chart"></div>
    <div class="controls">
      <button @click="generateData">生成数据</button>
      <button @click="runKMeans">运行K-means</button>
      <button @click="reset">重置</button>
      <div>
        <label>聚类数量: </label>
        <input type="number" v-model.number="k" min="1" max="10" />
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'KMeansVisualization',
  data() {
    return {
      k: 3, // 默认聚类数量
      dataPoints: [], // 数据点
      clusters: [], // 聚类中心
      svg: null, // D3 SVG对象
      width: 500, // 图表宽度
      height: 500, // 图表高度
      margin: 30, // 边距
      colorScale: d3.scaleOrdinal(d3.schemeCategory10) // 颜色比例尺
    };
  },
  mounted() {
    this.initChart();
    this.generateData();
  },
  methods: {
    // 初始化图表
    initChart() {
      this.svg = d3.select(this.$refs.chartContainer)
        .append('svg')
        .attr('width', this.width)
        .attr('height', this.height)
        .style('border', '1px solid #ccc');
    },
    
    // 生成随机数据
    generateData() {
      this.dataPoints = [];
      const clustersCount = 3;
      const pointsPerCluster = 30;
      
      for (let i = 0; i < clustersCount; i++) {
        const centerX = this.margin + Math.random() * (this.width - 2 * this.margin);
        const centerY = this.margin + Math.random() * (this.height - 2 * this.margin);
        
        for (let j = 0; j < pointsPerCluster; j++) {
          this.dataPoints.push({
            x: centerX + (Math.random() - 0.5) * 100,
            y: centerY + (Math.random() - 0.5) * 100,
            cluster: i
          });
        }
      }
      
      this.renderData();
    },
    
    // 渲染数据点
    renderData() {
      // 清除现有图形
      this.svg.selectAll('*').remove();
      
      // 创建比例尺
      const xScale = d3.scaleLinear()
        .domain([0, this.width])
        .range([this.margin, this.width - this.margin]);
      
      const yScale = d3.scaleLinear()
        .domain([0, this.height])
        .range([this.height - this.margin, this.margin]);
      
      // 绘制数据点
      this.svg.selectAll('circle.data-point')
        .data(this.dataPoints)
        .enter()
        .append('circle')
        .attr('class', 'data-point')
        .attr('cx', d => xScale(d.x))
        .attr('cy', d => yScale(d.y))
        .attr('r', 5)
        .attr('fill', d => this.colorScale(d.cluster))
        .attr('opacity', 0.7);
      
      // 如果有聚类中心，绘制中心点
      if (this.clusters.length > 0) {
        this.svg.selectAll('circle.cluster-center')
          .data(this.clusters)
          .enter()
          .append('circle')
          .attr('class', 'cluster-center')
          .attr('cx', d => xScale(d.x))
          .attr('cy', d => yScale(d.y))
          .attr('r', 10)
          .attr('fill', (d, i) => this.colorScale(i))
          .attr('stroke', '#000')
          .attr('stroke-width', 2);
      }
    },
    
    // 运行K-means算法
    runKMeans() {
      // 1. 随机初始化聚类中心
      this.clusters = [];
      for (let i = 0; i < this.k; i++) {
        this.clusters.push({
          x: this.margin + Math.random() * (this.width - 2 * this.margin),
          y: this.margin + Math.random() * (this.height - 2 * this.margin),
          points: []
        });
      }
      
      // 2. 执行几次迭代（简化版K-means）
      for (let iter = 0; iter < 5; iter++) {
        // 分配点到最近的聚类中心
        this.dataPoints.forEach(point => {
          let minDist = Infinity;
          let closestCluster = 0;
          
          this.clusters.forEach((cluster, idx) => {
            const dist = Math.sqrt(
              Math.pow(point.x - cluster.x, 2) + 
              Math.pow(point.y - cluster.y, 2)
            );
            
            if (dist < minDist) {
              minDist = dist;
              closestCluster = idx;
            }
          });
          
          point.cluster = closestCluster;
        });
        
        // 重新计算聚类中心
        this.clusters.forEach((cluster, idx) => {
          const pointsInCluster = this.dataPoints.filter(p => p.cluster === idx);
          if (pointsInCluster.length > 0) {
            cluster.x = d3.mean(pointsInCluster, p => p.x);
            cluster.y = d3.mean(pointsInCluster, p => p.y);
          }
        });
      }
      
      this.renderData();
    },
    
    // 重置图表
    reset() {
      this.clusters = [];
      this.generateData();
    }
  }
};
</script>

<style scoped>
.kmeans-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px;
}

.kmeans-chart {
  margin-bottom: 20px;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

button {
  padding: 5px 10px;
  cursor: pointer;
}

input {
  width: 50px;
  padding: 5px;
}
</style>