<template>
  <div class="code-debug-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>代码调试</h2>
          <el-select
            v-model="currentTemplate"
            placeholder="选择代码模板"
            @change="loadTemplate"
          >
            <el-option
              v-for="template in codeTemplates"
              :key="template.value"
              :label="template.label"
              :value="template.value"
            />
          </el-select>
        </div>
      </template>

      <div class="editor-container">
        <MonacoEditor
          v-model="code"
          language="python"
          :options="editorOptions"
          class="editor"
        />

        <div class="action-buttons">
          <el-button type="primary" @click="executeCode" :loading="isExecuting">
            运行代码
          </el-button>
          <el-button @click="resetCode">
            重置
          </el-button>
        </div>
      </div>

      <div class="output-container">
        <h3>运行结果</h3>
        <div class="output-content">
          <pre v-if="output">{{ output }}</pre>
          <el-empty v-else description="暂无执行结果" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElEmpty } from 'element-plus' // 关键修复
import MonacoEditor from '@/components/editor/MonacoEditor.vue'
import studentAPI from '@/api/student'

const code = ref('')
const output = ref('')
const currentTemplate = ref('kmeans')
const isExecuting = ref(false)

const codeTemplates = [
  { value: 'kmeans', label: 'K-Means 示例' },
  { value: 'dbscan', label: 'DBSCAN 示例' },
  { value: 'hierarchical', label: '层次聚类示例' }
]

const editorOptions = {
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 14,
  scrollBeyondLastLine: false
}

const loadTemplate = async () => {
  try {
    const response = await studentAPI.getAlgorithmContent(currentTemplate.value)
    code.value = response.data.codeTemplate || defaultTemplate(currentTemplate.value)
  } catch (error) {
    console.error('加载模板失败:', error)
    code.value = defaultTemplate(currentTemplate.value)
  }
}

const defaultTemplate = (algorithm) => {
  const templates = {
    kmeans: `# K-Means 聚类示例
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# 生成样本数据
X = np.array([[1, 2], [1, 4], [1, 0],
              [4, 2], [4, 4], [4, 0]])

# 创建KMeans实例并拟合数据
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

# 获取聚类标签和质心
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

# 输出结果
print("聚类标签:", labels)
print("质心位置:\\n", centroids)

# 可视化结果
plt.scatter(X[:, 0], X[:, 1], c=labels, s=50, cmap='viridis')
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=200, alpha=0.5)
plt.title('K-Means聚类结果')
plt.show()`,
    dbscan: `# DBSCAN 聚类示例
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons
import matplotlib.pyplot as plt

# 生成样本数据
X, y = make_moons(n_samples=200, noise=0.05, random_state=0)

# 创建DBSCAN实例并拟合数据
dbscan = DBSCAN(eps=0.3, min_samples=5)
clusters = dbscan.fit_predict(X)

# 输出结果
print("聚类标签:", clusters)
print("核心样本数量:", len(dbscan.core_sample_indices_))

# 可视化结果
plt.scatter(X[:, 0], X[:, 1], c=clusters, s=50, cmap='viridis')
plt.title('DBSCAN聚类结果')
plt.show()`,
    hierarchical: `# 层次聚类示例
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt

# 生成样本数据
X, y = make_blobs(n_samples=20, centers=3, n_features=2, random_state=0)

# 进行层次聚类
Z = linkage(X, 'ward')

# 绘制树状图
plt.figure(figsize=(10, 6))
dendrogram(Z)
plt.title('层次聚类树状图')
plt.xlabel('样本索引')
plt.ylabel('距离')
plt.show()`
  }

  return templates[algorithm] || '请选择代码模板'
}

const executeCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入要执行的代码')
    return
  }

  isExecuting.value = true
  output.value = ''

  try {
    const response = await studentAPI.executeCode({
      code: code.value,
      algorithm: currentTemplate.value
    })
    output.value = response.data.output
  } catch (error) {
    output.value = `执行错误: ${error.response?.data?.message || error.message}`
  } finally {
    isExecuting.value = false
  }
}

const resetCode = () => {
  code.value = defaultTemplate(currentTemplate.value)
  output.value = ''
}

// 初始化加载模板
loadTemplate()
</script>

<style scoped>
.code-debug-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.editor-container {
  margin-bottom: 20px;
  border: 1px solid #eee;
  border-radius: 4px;
  overflow: hidden;
}

.editor {
  height: 400px;
}

.action-buttons {
  padding: 10px;
  background: #f5f7fa;
  text-align: right;
}

.output-container {
  margin-top: 20px;
}

.output-content {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
  min-height: 100px;
  max-height: 300px;
  overflow-y: auto;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
