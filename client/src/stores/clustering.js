import { defineStore } from 'pinia';
import { simulateAlgorithm, getDataTypes, getCentroidMethods } from '@/api/clustering';

export const useClusteringStore = defineStore('clustering', {
  state: () => ({
    algorithm: null,
    dataPoints: [],
    clusters: [],
    simulationData: null,
    currentStep: 0,
    dataTypes: [],
    centroidMethods: [],
  }),
  actions: {
    async simulateAlgorithm(algorithm, params) {
      try {
        console.log('Store: 开始模拟算法', algorithm, params);
        this.algorithm = algorithm;
        
        // 如果是开发模式，使用模拟数据
        if (process.env.NODE_ENV === 'development') {
          console.log('开发模式：使用模拟数据');
          return this.useMockData(algorithm, params);
        }
        
        const response = await simulateAlgorithm(algorithm, params);
        console.log('Store: 收到响应', response.data);
        
        this.simulationData = response.data;
        this.currentStep = 0;
        
        console.log('Store: 设置完成', this.simulationData);
        return response.data;
      } catch (error) {
        console.error('Store: 模拟错误', error);
        // 开发环境下使用模拟数据
        if (process.env.NODE_ENV === 'development') {
          console.log('使用模拟数据作为降级方案');
          return this.useMockData(algorithm, params);
        }
        const errorMsg = error.response?.data?.error || error.message || '模拟失败';
        throw new Error(errorMsg);
      }
    },
    
    // 模拟数据生成方法
    useMockData(algorithm, params) {
      const pointCount = params.point_count || 150;
      const kValue = params.k_value || 3;
      const dataType = params.data_type || 'gaussian';
      const customCentroids = params.custom_centroids; // 添加自定义质心参数
       // 添加 DBSCAN 参数获取
      const epsilon = params.epsilon || 0.5;        // 从 params 获取 epsilon
      const minPoints = params.min_points || 5;     // 从 params 获取 minPoints
  
      if (algorithm === 'kmeans') {
        const fixedPoints = this.generateFixedPoints(pointCount, dataType, kValue);
        
        // 如果有自定义质心，使用自定义位置
        if (customCentroids && customCentroids.length > 0) {
          this.simulationData = this.generateKMeansDataWithCustomCentroids(
            fixedPoints, 
            customCentroids
          );
        } else {
          this.simulationData = this.generateKMeansData(fixedPoints, kValue, params.centroid_method);
        }
    } else if (algorithm === 'dbscan') {
        const fixedPoints = this.generateFixedPoints(pointCount, dataType, 3);
        this.simulationData = this.generateDBSCANData(fixedPoints, epsilon, minPoints);
      // 在 useMockData 方法中添加
    } else if (algorithm === 'gmm') {
      const fixedPoints = this.generateFixedPoints(pointCount, dataType, params.k_value || 3);
      this.simulationData = this.generateGMMData(
        fixedPoints, 
        params.k_value || 3,
        params.covariance_type || 'full',
        params.max_iterations || 100,
        params.tolerance || 0.001
      );
    }
      this.currentStep = 0;
      return this.simulationData;
    },
    // 添加支持自定义质心的K-Means生成方法
    generateKMeansDataWithCustomCentroids(fixedPoints, customCentroids) {
      const steps = [];
      const kValue = customCentroids.length;
      
      // 步骤1: 初始状态
      steps.push({
        centroids: [],
        description: "初始数据点（未分类）",
        points: fixedPoints.map(p => ({ ...p, cluster: -1 })),
        metrics: {}
      });

      // 步骤2: 显示自定义质心
      const initialCentroids = customCentroids.map((pos, index) => ({
        cluster: index,
        x: pos.x,
        y: pos.y
      }));
      
      steps.push({
        centroids: [...initialCentroids],
        description: "使用自定义质心位置",
        points: fixedPoints.map(p => ({ ...p, cluster: -1 })),
        metrics: {}
      });

      // 后续迭代步骤（与之前相同）
      let currentCentroids = [...initialCentroids];
      
      for (let iter = 1; iter <= 5; iter++) {
        // 分配点到最近的质心
        const assignedPoints = fixedPoints.map(point => {
          let minDistance = Infinity;
          let assignedCluster = -1;
          
          currentCentroids.forEach(centroid => {
            const distance = Math.sqrt(
              Math.pow(point.x - centroid.x, 2) + 
              Math.pow(point.y - centroid.y, 2)
            );
            
            if (distance < minDistance) {
              minDistance = distance;
              assignedCluster = centroid.cluster;
            }
          });
          
          return {
            ...point,
            cluster: assignedCluster
          };
        });

        // 计算新的质心位置
        const newCentroids = [];
        for (let i = 0; i < kValue; i++) {
          const clusterPoints = assignedPoints.filter(p => p.cluster === i);
          if (clusterPoints.length > 0) {
            const sumX = clusterPoints.reduce((sum, p) => sum + p.x, 0);
            const sumY = clusterPoints.reduce((sum, p) => sum + p.y, 0);
            newCentroids.push({
              cluster: i,
              x: sumX / clusterPoints.length,
              y: sumY / clusterPoints.length
            });
          } else {
            newCentroids.push({
              cluster: i,
              x: currentCentroids[i].x,
              y: currentCentroids[i].y
            });
          }
        }

        steps.push({
          centroids: [...newCentroids],
          description: `迭代 ${iter}: 分配点到质心并更新质心位置`,
          points: assignedPoints,
          metrics: {
            inertia: this.calculateSSE(assignedPoints, newCentroids)
          }
        });

        currentCentroids = newCentroids;
      }

      // 计算最终指标
      const sse = this.calculateSSE(steps[steps.length - 1].points, currentCentroids);
      const silhouette = 0.4 + Math.random() * 0.3;

      return {
        algorithm: "kmeans",
        metrics: {
          silhouette: parseFloat(silhouette.toFixed(4)),
          sse: parseFloat(sse.toFixed(2)),
          iterations: 5
        },
        status: "success",
        steps: steps
      };
    },
        // 生成固定的数据点
    generateFixedPoints(pointCount, dataType, clusterCount) {
      const points = [];
      
      console.log('🔄 generateFixedPoints 调用:', { pointCount, dataType, clusterCount });
      
      if (dataType === 'gaussian') {
        // 生成高斯分布的数据点
        const centers = [];
        for (let i = 0; i < clusterCount; i++) {
          centers.push({
            x: 2 + Math.random() * 6,
            y: 2 + Math.random() * 6,
            cluster: i
          });
        }
        
        const pointsPerCluster = Math.floor(pointCount / clusterCount);
        
        centers.forEach(center => {
          for (let i = 0; i < pointsPerCluster; i++) {
            points.push({
              x: center.x + (Math.random() - 0.5) * 1.5,
              y: center.y + (Math.random() - 0.5) * 1.5,
              cluster: center.cluster,
              originalCluster: center.cluster
            });
          }
        });
        
        // 添加剩余的点
        while (points.length < pointCount) {
          const randomCenter = centers[Math.floor(Math.random() * centers.length)];
          points.push({
            x: randomCenter.x + (Math.random() - 0.5) * 1.5,
            y: randomCenter.y + (Math.random() - 0.5) * 1.5,
            cluster: randomCenter.cluster,
            originalCluster: randomCenter.cluster
          });
        }
        
      } else if (dataType === 'uniform') {
        // 均匀分布
        for (let i = 0; i < pointCount; i++) {
          points.push({
            x: Math.random() * 8 + 1,
            y: Math.random() * 8 + 1,
            cluster: -1,
            originalCluster: -1
          });
        }
      } else if (dataType === 'moons') {
        // 月牙形分布
        const half = Math.floor(pointCount / 2);
        for (let i = 0; i < half; i++) {
          const angle = Math.PI * Math.random();
          const radius = 0.5 + Math.random() * 0.3;
          points.push({
            x: 3 + Math.cos(angle) * radius,
            y: 5 + Math.sin(angle) * radius,
            cluster: 0,
            originalCluster: 0
          });
        }
        for (let i = half; i < pointCount; i++) {
          const angle = Math.PI * Math.random();
          const radius = 0.5 + Math.random() * 0.3;
          points.push({
            x: 7 + Math.cos(angle) * radius,
            y: 5 + Math.sin(angle) * radius,
            cluster: 1,
            originalCluster: 1
          });
        }
      } else if (dataType === 'circles') {
        // 环形分布
        const half = Math.floor(pointCount / 2);
        for (let i = 0; i < half; i++) {
          const angle = 2 * Math.PI * Math.random();
          const radius = 1.5 + Math.random() * 0.5;
          points.push({
            x: 5 + Math.cos(angle) * radius,
            y: 5 + Math.sin(angle) * radius,
            cluster: 0,
            originalCluster: 0
          });
        }
        for (let i = half; i < pointCount; i++) {
          const angle = 2 * Math.PI * Math.random();
          const radius = 3.0 + Math.random() * 0.5;
          points.push({
            x: 5 + Math.cos(angle) * radius,
            y: 5 + Math.sin(angle) * radius,
            cluster: 1,
            originalCluster: 1
          });
        }
    } else if (dataType === 'smiley') {
  // 笑脸分布 - 修正版
  console.log('🎭 生成笑脸分布数据');
  
  // 脸轮廓 (大圆)
  const nFace = Math.floor(pointCount * 0.5);
  for (let i = 0; i < nFace; i++) {
    const angle = Math.random() * 2 * Math.PI;
    const radius = 3.5 + Math.random() * 1.0;
    points.push({
      x: 5 + radius * Math.cos(angle),
      y: 5 + radius * Math.sin(angle),
      cluster: 0,
      originalCluster: 0
    });
  }
  
  // 左眼 (小圆)
  const nEye = Math.floor(pointCount * 0.125);
  for (let i = 0; i < nEye; i++) {
    const angle = Math.random() * 2 * Math.PI;
    const radius = 0.4 + Math.random() * 0.2;
    points.push({
      x: 3.5 + radius * Math.cos(angle),
      y: 6 + radius * Math.sin(angle),
      cluster: 1,
      originalCluster: 1
    });
  }
  
  // 右眼 (小圆)
  for (let i = 0; i < nEye; i++) {
    const angle = Math.random() * 2 * Math.PI;
    const radius = 0.4 + Math.random() * 0.2;
    points.push({
      x: 6.5 + radius * Math.cos(angle),
      y: 6 + radius * Math.sin(angle),
      cluster: 2,
      originalCluster: 2
    });
  }
  
  // 嘴巴 (向下弧形) - 关键修正！
  const nMouth = pointCount - nFace - 2 * nEye;
  for (let i = 0; i < nMouth; i++) {
    // 使用下半圆的角度范围：π 到 2π (180° 到 360°)
    const angle = Math.PI + Math.random() * Math.PI;
    const radius = 1.5 + Math.random() * 0.5;  // 减小半径
    
    points.push({
      x: 5 + radius * Math.cos(angle),
      y: 4.5 + radius * Math.sin(angle),  // 中心点下移
      cluster: 3,
      originalCluster: 3
    });
  }
}else if (dataType === 'noisy') {
        // 噪声分布 - 简化版前端实现
        console.log('🔊 生成噪声分布数据');
        
        // 先生成正常聚类数据
        const nClusterPoints = Math.floor(pointCount * 0.75);
        const nNoisePoints = pointCount - nClusterPoints;
        
        const centers = [];
        for (let i = 0; i < 3; i++) {
          centers.push({
            x: 2 + Math.random() * 6,
            y: 2 + Math.random() * 6,
            cluster: i
          });
        }
        
        const pointsPerCluster = Math.floor(nClusterPoints / 3);
        
        centers.forEach(center => {
          for (let i = 0; i < pointsPerCluster; i++) {
            points.push({
              x: center.x + (Math.random() - 0.5) * 1.5,
              y: center.y + (Math.random() - 0.5) * 1.5,
              cluster: center.cluster,
              originalCluster: center.cluster
            });
          }
        });
        
        // 添加噪声点
        for (let i = 0; i < nNoisePoints; i++) {
          points.push({
            x: Math.random() * 10,
            y: Math.random() * 10,
            cluster: -1, // -1 表示噪声点
            originalCluster: -1
          });
        }
        
      } else {
        // 未知数据类型，使用均匀分布作为后备
        console.warn(`⚠️ 未知数据类型: ${dataType}, 使用均匀分布`);
        for (let i = 0; i < pointCount; i++) {
          points.push({
            x: Math.random() * 8 + 1,
            y: Math.random() * 8 + 1,
            cluster: -1,
            originalCluster: -1
          });
        }
      }
      
      // 确保所有点都在可见范围内 (1-9)
      points.forEach(point => {
        point.x = Math.max(1, Math.min(9, point.x));
        point.y = Math.max(1, Math.min(9, point.y));
      });
      
      // 打乱点顺序
      for (let i = points.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [points[i], points[j]] = [points[j], points[i]];
      }
      
      console.log(`✅ 生成完成: ${points.length} 个点`);
      if (points.length > 0) {
        console.log(`📍 第一个点: (${points[0].x.toFixed(2)}, ${points[0].y.toFixed(2)})`);
      }
      
      return points;
    },
    
    // 正确的K-Means模拟
    generateKMeansData(fixedPoints, kValue) {
      const steps = [];
      
      // 步骤1: 初始状态，所有点未分类
      steps.push({
        centroids: [],
        description: "初始数据点（未分类）",
        points: fixedPoints.map(p => ({ ...p, cluster: -1 })),
        metrics: {}
      });

      // 随机选择初始质心（从现有点中选择）
      const initialCentroids = [];
      const indices = new Set();
      while (indices.size < kValue && indices.size < fixedPoints.length) {
        const randomIndex = Math.floor(Math.random() * fixedPoints.length);
        if (!indices.has(randomIndex)) {
          indices.add(randomIndex);
          const point = fixedPoints[randomIndex];
          initialCentroids.push({
            cluster: initialCentroids.length,
            x: point.x,
            y: point.y
          });
        }
      }

      // 步骤2: 显示初始质心
      steps.push({
        centroids: [...initialCentroids],
        description: "随机选择初始质心",
        points: fixedPoints.map(p => ({ ...p, cluster: -1 })),
        metrics: {}
      });

      let currentCentroids = [...initialCentroids];
      let previousPoints = fixedPoints.map(p => ({ ...p, cluster: -1 }));
      
      // 模拟迭代过程
      for (let iter = 1; iter <= 5; iter++) {
        // 分配点到最近的质心
        const assignedPoints = fixedPoints.map(point => {
          let minDistance = Infinity;
          let assignedCluster = -1;
          
          currentCentroids.forEach(centroid => {
            const distance = Math.sqrt(
              Math.pow(point.x - centroid.x, 2) + 
              Math.pow(point.y - centroid.y, 2)
            );
            
            if (distance < minDistance) {
              minDistance = distance;
              assignedCluster = centroid.cluster;
            }
          });
          
          return {
            ...point,
            cluster: assignedCluster
          };
        });

        // 计算新的质心位置
        const newCentroids = [];
        for (let i = 0; i < kValue; i++) {
          const clusterPoints = assignedPoints.filter(p => p.cluster === i);
          if (clusterPoints.length > 0) {
            const sumX = clusterPoints.reduce((sum, p) => sum + p.x, 0);
            const sumY = clusterPoints.reduce((sum, p) => sum + p.y, 0);
            newCentroids.push({
              cluster: i,
              x: sumX / clusterPoints.length,
              y: sumY / clusterPoints.length
            });
          } else {
            // 如果簇没有点，保持原位置
            const oldCentroid = currentCentroids.find(c => c.cluster === i);
            newCentroids.push({
              cluster: i,
              x: oldCentroid ? oldCentroid.x : Math.random() * 8 + 1,
              y: oldCentroid ? oldCentroid.y : Math.random() * 8 + 1
            });
          }
        }

        // 添加步骤
        steps.push({
          centroids: [...newCentroids],
          description: `迭代 ${iter}: 分配点到质心并更新质心位置`,
          points: assignedPoints,
          metrics: {
            inertia: this.calculateSSE(assignedPoints, newCentroids)
          }
        });

        currentCentroids = newCentroids;
        previousPoints = assignedPoints;
      }

      // 计算最终指标
      const sse = this.calculateSSE(previousPoints, currentCentroids);
      const silhouette = 0.4 + Math.random() * 0.3;

      return {
        algorithm: "kmeans",
        metrics: {
          silhouette: parseFloat(silhouette.toFixed(4)),
          sse: parseFloat(sse.toFixed(2)),
          iterations: 5
        },
        status: "success",
        steps: steps
      };
    },
    
    // DBSCAN模拟
    generateDBSCANData(fixedPoints, epsilon, minPoints) {
      const steps = [];
      
      // 步骤1: 初始状态
      steps.push({
        description: "初始数据点（未分类）",
        points: fixedPoints.map(p => ({ ...p, cluster: -1 })),
        metrics: {}
      });
      
      // 简化的DBSCAN实现
      let clusterId = 0;
      const visited = new Set();
      const clusteredPoints = fixedPoints.map(p => ({ ...p, cluster: -1 }));
      
      for (let i = 0; i < clusteredPoints.length; i++) {
        if (visited.has(i)) continue;
        
        visited.add(i);
        const neighbors = this.findNeighbors(clusteredPoints, i, epsilon);
        
        if (neighbors.length < minPoints) {
          // 噪声点
          clusteredPoints[i].cluster = -1;
        } else {
          // 新簇
          clusterId++;
          clusteredPoints[i].cluster = clusterId;
          
          // 扩展簇
          let queue = [...neighbors];
          while (queue.length > 0) {
            const neighborIndex = queue.shift();
            if (visited.has(neighborIndex)) continue;
            
            visited.add(neighborIndex);
            const neighborNeighbors = this.findNeighbors(clusteredPoints, neighborIndex, epsilon);
            
            if (neighborNeighbors.length >= minPoints) {
              queue = queue.concat(neighborNeighbors.filter(idx => !visited.has(idx)));
            }
            
            if (clusteredPoints[neighborIndex].cluster === -1) {
              clusteredPoints[neighborIndex].cluster = clusterId;
            }
          }
        }
      }
      
      // 步骤2: 聚类结果
      steps.push({
        description: "DBSCAN聚类完成",
        points: clusteredPoints,
        metrics: {
          clusters: clusterId,
          noise_points: clusteredPoints.filter(p => p.cluster === -1).length
        }
      });
      
      return {
        algorithm: "dbscan",
        metrics: {
          silhouette: parseFloat((0.3 + Math.random() * 0.2).toFixed(4)),
          clusters: clusterId,
          noise_points: clusteredPoints.filter(p => p.cluster === -1).length
        },
        status: "success",
        steps: steps
      };
    },
    
    // 初始化协方差矩阵
    initializeCovariances(kValue, covarianceType) {
      const covariances = [];
      for (let i = 0; i < kValue; i++) {
        if (covarianceType === 'full') {
          covariances.push([[1, 0], [0, 1]]); // 单位矩阵
        } else if (covarianceType === 'diag') {
          covariances.push([[1, 0], [0, 1]]); // 对角矩阵
        } else if (covarianceType === 'spherical') {
          covariances.push([[1, 0], [0, 1]]); // 球面矩阵
        } else if (covarianceType === 'tied') {
          // 所有分量共享同一个协方差矩阵
          return Array(kValue).fill([[1, 0], [0, 1]]);
        }
      }
      return covariances;
    },

    // 计算概率
    calculateProbabilities(point, means, covariances, weights) {
      const probabilities = [];
      let total = 0;
      
      for (let i = 0; i < means.length; i++) {
        // 简化的概率计算（实际应使用多元高斯分布）
        const distance = Math.sqrt(
          Math.pow(point.x - means[i].x, 2) + 
          Math.pow(point.y - means[i].y, 2)
        );
        const probability = weights[i] * Math.exp(-distance * distance / 2);
        probabilities.push(probability);
        total += probability;
      }
      
      // 归一化
      return probabilities.map(p => p / total);
    },

    // 更新权重
    updateWeights(points, kValue) {
      const weights = Array(kValue).fill(0);
      let total = 0;
      
      points.forEach(point => {
        if (point.cluster >= 0 && point.cluster < kValue) {
          weights[point.cluster] += point.probability || 1;
          total += point.probability || 1;
        }
      });
      
      return weights.map(w => w / total);
    },

    // 更新均值
    updateMeans(points, kValue) {
      const means = Array(kValue).fill({ x: 0, y: 0 });
      const counts = Array(kValue).fill(0);
      
      points.forEach(point => {
        if (point.cluster >= 0 && point.cluster < kValue) {
          const weight = point.probability || 1;
          means[point.cluster] = {
            x: (means[point.cluster].x || 0) + point.x * weight,
            y: (means[point.cluster].y || 0) + point.y * weight
          };
          counts[point.cluster] += weight;
        }
      });
      
      return means.map((mean, i) => ({
        cluster: i,
        x: counts[i] > 0 ? mean.x / counts[i] : (Math.random() * 8 + 1),
        y: counts[i] > 0 ? mean.y / counts[i] : (Math.random() * 8 + 1)
      }));
    },

    // 更新协方差矩阵（简化实现）
    updateCovariances(points, means, kValue, covarianceType) {
      // 返回初始协方差矩阵（简化实现）
      return this.initializeCovariances(kValue, covarianceType);
    },

    // 计算对数似然（简化实现）
    calculateLogLikelihood(points, means, covariances, weights) {
      return -1000 + Math.random() * 500; // 随机值
    },

    // 计算BIC（简化实现）
    calculateBIC(points, means, covariances, weights) {
      const n = points.length;
      const k = means.length * 3; // 参数数量（均值x,y + 权重）
      const logLikelihood = this.calculateLogLikelihood(points, means, covariances, weights);
      return k * Math.log(n) - 2 * logLikelihood;
    },

    // 计算AIC（简化实现）
    calculateAIC(points, means, covariances, weights) {
      const k = means.length * 3; // 参数数量
      const logLikelihood = this.calculateLogLikelihood(points, means, covariances, weights);
      return 2 * k - 2 * logLikelihood;
    },
    // 添加 GMM 模拟方法
    generateGMMData(fixedPoints, kValue, covarianceType, maxIterations, tolerance) {
      const steps = [];
      
      // 步骤1: 初始状态
      steps.push({
        centroids: [],
        description: "初始数据点（未分类）",
        points: fixedPoints.map(p => ({ ...p, cluster: -1, probability: 0 })),
        metrics: {}
      });

      // 初始化高斯分布参数
      const initialMeans = [];
      const indices = new Set();
      while (indices.size < kValue && indices.size < fixedPoints.length) {
        const randomIndex = Math.floor(Math.random() * fixedPoints.length);
        if (!indices.has(randomIndex)) {
          indices.add(randomIndex);
          const point = fixedPoints[randomIndex];
          initialMeans.push({
            cluster: initialMeans.length,
            x: point.x,
            y: point.y
          });
        }
      }

      // 步骤2: 显示初始均值
      steps.push({
        centroids: [...initialMeans],
        description: "初始化高斯分布均值",
        points: fixedPoints.map(p => ({ ...p, cluster: -1, probability: 0 })),
        metrics: {}
      });

      let currentMeans = [...initialMeans];
      let currentCovariances = this.initializeCovariances(kValue, covarianceType);
      let currentWeights = Array(kValue).fill(1 / kValue);
      
      // 模拟EM算法迭代过程
      for (let iter = 1; iter <= 5; iter++) {
        // E步骤: 计算响应度（后验概率）
        const eStepPoints = fixedPoints.map(point => {
          const probabilities = this.calculateProbabilities(
            point, currentMeans, currentCovariances, currentWeights
          );
          
          // 找到概率最大的簇
          let maxProb = 0;
          let assignedCluster = -1;
          
          probabilities.forEach((prob, cluster) => {
            if (prob > maxProb) {
              maxProb = prob;
              assignedCluster = cluster;
            }
          });
          
          return {
            ...point,
            cluster: assignedCluster,
            probability: maxProb
          };
        });

        // M步骤: 更新参数
        const newWeights = this.updateWeights(eStepPoints, kValue);
        const newMeans = this.updateMeans(eStepPoints, kValue);
        const newCovariances = this.updateCovariances(
          eStepPoints, newMeans, kValue, covarianceType
        );

        // 添加步骤
        steps.push({
          centroids: [...newMeans],
          description: `EM迭代 ${iter}: 更新高斯分布参数`,
          points: eStepPoints,
          metrics: {
            log_likelihood: this.calculateLogLikelihood(
              fixedPoints, newMeans, newCovariances, newWeights
            )
          }
        });

        currentMeans = newMeans;
        currentCovariances = newCovariances;
        currentWeights = newWeights;
      }

      // 计算最终指标
      const finalPoints = steps[steps.length - 1].points;
      const silhouette = 0.5 + Math.random() * 0.3;
      const bic = this.calculateBIC(finalPoints, currentMeans, currentCovariances, currentWeights);
      const aic = this.calculateAIC(finalPoints, currentMeans, currentCovariances, currentWeights);

      return {
        algorithm: "gmm",
        metrics: {
          silhouette: parseFloat(silhouette.toFixed(4)),
          bic: parseFloat(bic.toFixed(2)),
          aic: parseFloat(aic.toFixed(2)),
          iterations: 5,
          converged: true
        },
        status: "success",
        steps: steps
      };
    },
// 计算高斯分布概率
    calculateGaussianProbability(point, gaussian) {
      const dx = point.x - gaussian.mean.x;
      const dy = point.y - gaussian.mean.y;
      
      // 简化计算：假设协方差矩阵是对角矩阵
      const det = gaussian.covariance[0][0] * gaussian.covariance[1][1];
      const invCov = [
        [1 / gaussian.covariance[0][0], 0],
        [0, 1 / gaussian.covariance[1][1]]
      ];
      
      const exponent = -0.5 * (
        dx * dx * invCov[0][0] + 
        dy * dy * invCov[1][1]
      );
      
      return gaussian.weight * Math.exp(exponent) / (2 * Math.PI * Math.sqrt(det));
    },

 



    
    // 查找邻居点（DBSCAN用）
    findNeighbors(points, index, epsilon) {
      const neighbors = [];
      const point = points[index];
      
      for (let i = 0; i < points.length; i++) {
        if (i === index) continue;
        
        const distance = Math.sqrt(
          Math.pow(point.x - points[i].x, 2) + 
          Math.pow(point.y - points[i].y, 2)
        );
        
        if (distance <= epsilon) {
          neighbors.push(i);
        }
      }
      
      return neighbors;
    },
    
    // 计算SSE（Sum of Squared Errors）
    calculateSSE(points, centroids) {
      let sse = 0;
      
      points.forEach(point => {
        const centroid = centroids.find(c => c.cluster === point.cluster);
        if (centroid) {
          const distance = Math.sqrt(
            Math.pow(point.x - centroid.x, 2) + 
            Math.pow(point.y - centroid.y, 2)
          );
          sse += distance * distance;
        }
      });
      
      return sse;
    },
    
    reset() {
      this.simulationData = null;
      this.currentStep = 0;
    },
    
    async fetchDataTypes() {
  try {
    // 更新后的数据类型列表
    this.dataTypes = [
      { 
        value: 'uniform', 
        label: '均匀分布', 
        description: '数据点在整个空间均匀分布', 
        supported_algorithms: ['kmeans', 'dbscan', 'gmm'] 
      },
      { 
        value: 'gaussian', 
        label: '高斯分布', 
        description: '数据点呈高斯分布，形成自然簇', 
        supported_algorithms: ['kmeans', 'gmm'] 
      },
      { 
        value: 'moons', 
        label: '月牙分布', 
        description: '数据点形成月牙形结构', 
        supported_algorithms: ['dbscan'] 
      },
      { 
        value: 'circles', 
        label: '环形分布', 
        description: '数据点形成环形结构', 
        supported_algorithms: ['dbscan'] 
      },
      { 
        value: 'smiley', 
        label: '笑脸分布', 
        description: '数据点形成笑脸形状，测试复杂结构识别', 
        supported_algorithms: ['dbscan', 'gmm'] 
      },
      { 
        value: 'spiral', 
        label: '螺旋分布', 
        description: '数据点形成螺旋结构，测试非线性分离', 
        supported_algorithms: ['dbscan'] 
      },
      { 
        value: 'anisotropic', 
        label: '异方差分布', 
        description: '不同方向方差不同的高斯分布', 
        supported_algorithms: ['kmeans', 'gmm'] 
      },
      { 
        value: 'noisy', 
        label: '噪声分布', 
        description: '包含大量噪声点的数据集', 
        supported_algorithms: ['dbscan'] 
      }
    ];
  } catch (error) {
    console.error('获取数据类型失败:', error);
    // 降级方案 - 保留基本的数据类型
    this.dataTypes = [
      { 
        value: 'uniform', 
        label: '均匀分布', 
        description: '数据点在整个空间均匀分布',
        supported_algorithms: ['kmeans', 'dbscan', 'gmm']
      },
      { 
        value: 'gaussian', 
        label: '高斯分布', 
        description: '数据点呈高斯分布，形成自然簇',
        supported_algorithms: ['kmeans', 'gmm']
      },
      { 
        value: 'moons', 
        label: '月牙分布', 
        description: '数据点形成月牙形结构',
        supported_algorithms: ['dbscan']
      },
      { 
        value: 'circles', 
        label: '环形分布', 
        description: '数据点形成环形结构',
        supported_algorithms: ['dbscan']
      }
    ];
  }
},
    



    async fetchCentroidMethods() {
      try {
        this.centroidMethods = [
          { value: 'random', label: '随机选择', description: '随机初始化质心', supported_algorithms: ['kmeans'] },
          { value: 'k-means++', label: 'K-Means++', description: '优化质心初始化', supported_algorithms: ['kmeans'] }
        ];
      } catch (error) {
        console.error('获取质心方法失败:', error);
        this.centroidMethods = [
          { value: 'random', label: '随机选择', description: '随机初始化质心' },
          { value: 'k-means++', label: 'K-Means++', description: '优化质心初始化' },
        ];
      }
    },
  },
});