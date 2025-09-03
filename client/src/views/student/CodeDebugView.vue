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

.code-debug-view ::v-deep(.el-card) {
  border-radius: 20px;
  box-shadow: 
    0 25px 50px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.05);
  border: none;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
}

.code-debug-view ::v-deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 30px;
  background: rgba(255, 255, 255, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-header h2 {
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-cl极光: text;
  font-size: 24px;
  font-weight: 600;
}

.code-debug-view ::v-deep(.el-select) {
  width: 200px;
}

.code-debug-view ::v-deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  box-shadow: none;
}

.code-de极光-view ::v-deep(.el-select .el-input__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.code-debug-view ::v-deep(.el-select .el-input__suffix) {
  color: rgba(255, 255, 255, 极光.7);
}

.code-debug-view ::v-deep(.el-select-dropdown) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.code-debug-view ::v-deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8);
}

.code-debug-view ::v-deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.2);
  color: #fff;
}

.code-debug-view ::v-deep(.el-select-dropdown__item.selected) {
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.editor-container {
  margin-bottom: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.editor {
  height: 400px;
}

.code-debug-view ::v-deep(.monaco-editor) {
  background: rgba(255, 255, 255, 0.02);
}

.code-debug-view ::v-deep(.monaco-editor .margin) {
  background: rgba(255, 255, 255, 0.03);
}

.action-buttons {
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  text-align: right;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.code-debug-view ::v-deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #9b59b6 100%);
  border: none;
  border-radius: 12px;
  height: 40px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.code-debug-view ::v-deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.code-debug-view ::v-deep(.el-button) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  height: 40px;
  transition: all 0.3s ease;
}

.code-debug-view ::v-deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.output-container {
  margin-top: 25px;
}

.output-container h3 {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 600;
}

.output-content {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 120px;
  max-height: 300px;
  overflow-y: auto;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  color: rgba(255, 255, 255, 0.8);
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
  margin: 0;
}

.empty-state ::v-deep(.el-empty__description) {
  color: rgba(255, 255, 255, 0.6);
}

.empty-state ::v-deep(.el-empty__image) {
  opacity: 0.5;
}
</style>
