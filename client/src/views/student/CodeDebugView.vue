<template>
  <div class="code-debug-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>代码调试</h2>
          <el-select
            v-model="currentAlgorithm"
            placeholder="选择算法"
            @change="loadTemplate"
          >
            <el-option
              v-for="algorithm in algorithms"
              :key="algorithm.value"
              :label="algorithm.label"
              :value="algorithm.value"
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
import { ref, onMounted } from 'vue'
import { ElMessage, ElEmpty } from 'element-plus'
import MonacoEditor from '@/components/editor/MonacoEditor.vue'
import studentApi from '@/api/student'

const code = ref('')
const output = ref('')
const currentAlgorithm = ref('kmeans')
const isExecuting = ref(false)

const algorithms = [
  { value: 'kmeans', label: 'K-Means 聚类' },
  { value: 'dbscan', label: 'DBSCAN 聚类' },
  { value: 'hierarchical', label: '高斯混合聚类GMM' }
]

const editorOptions = {
  automaticLayout: true,
  minimap: { enabled: false },
  fontSize: 14,
  scrollBeyondLastLine: false
}

const loadTemplate = async (algorithm = null) => {
  const algo = algorithm || currentAlgorithm.value
  try {
    console.log('正在加载算法模板:', algo)
    const response = await studentApi.getAlgorithmContent(algo)
    console.log('模板响应:', response)

    // 安全地访问模板数据
    if (response && response.codeTemplate) {
      code.value = response.codeTemplate
    } else if (response && typeof response === 'object') {
      // 尝试不同的属性名
      code.value = response.template || response.content || defaultTemplate(algo)
    } else {
      code.value = defaultTemplate(algo)
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    code.value = defaultTemplate(algo)
    ElMessage.warning('使用默认代码模板')
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

    gmm: `# 高斯混合聚类(GMM)示例
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
from scipy import linalg
import itertools

# 生成样本数据
X, y_true = make_blobs(n_samples=400, centers=4,
                       cluster_std=0.60, random_state=0)
X = X[:, ::-1]  # 翻转坐标轴以便更好地绘图

# 创建GMM实例并拟合数据
gmm = GaussianMixture(n_components=4, random_state=42)
gmm.fit(X)
labels = gmm.predict(X)

# 输出结果
print("聚类完成!")
print("每个高斯分布的权重:", gmm.weights_)
print("每个高斯分布的均值:\\n", gmm.means_)
print("收敛所需的迭代次数:", gmm.n_iter_)
print("BIC值:", gmm.bic(X))
print("AIC值:", gmm.aic(X))

# 可视化结果
plt.figure(figsize=(10, 8))

# 绘制数据点
plt.scatter(X[:, 0], X[:, 1], c=labels, s=40, cmap='viridis', zorder=2)

# 绘制高斯分布的椭圆
def plot_ellipses(ax, weights, means, covars):
    for n in range(len(weights)):
        if covars[n].shape == (2, 2):
            v, w = linalg.eigh(covars[n])
            u = w[0] / linalg.norm(w[0])
            angle = np.arctan2(u[1], u[0])
            angle = 180 * angle / np.pi  # 转换为度
            v = 2. * np.sqrt(2.) * np.sqrt(v)
            ell = plt.matplotlib.patches.Ellipse(means[n], v[0], v[1],
                                                180 + angle, color='red',
                                                alpha=weights[n] * 2)
            ell.set_clip_box(ax.bbox)
            ell.set_alpha(0.3)
            ax.add_artist(ell)

plot_ellipses(plt.gca(), gmm.weights_, gmm.means_, gmm.covariances_)

plt.title('高斯混合聚类(GMM)结果')
plt.xlabel('特征 1')
plt.ylabel('特征 2')
plt.grid(True, alpha=0.3)
plt.show()

# 概率预测示例
probs = gmm.predict_proba(X)
print("前5个样本属于各个簇的概率:\\n", probs[:5])`
  }

  return templates[algorithm] || '# 请选择算法并编写代码'
}


const executeCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入要执行的代码')
    return
  }

  isExecuting.value = true
  output.value = '执行中...'

  try {
    const response = await studentApi.executeCode({
      code: code.value,
      algorithm: currentAlgorithm.value
    })

    // 安全地处理响应
    if (response && response.output) {
      output.value = response.output
    } else if (response && typeof response === 'object') {
      output.value = JSON.stringify(response, null, 2)
    } else {
      output.value = '执行完成，无输出结果'
    }

    ElMessage.success('代码执行成功')
  } catch (error) {
    console.error('执行错误:', error)
    output.value = `执行错误: ${error.response?.data?.error || error.message || '未知错误'}`
    ElMessage.error('代码执行失败')
  } finally {
    isExecuting.value = false
  }
}

const resetCode = () => {
  code.value = defaultTemplate(currentAlgorithm.value)
  output.value = ''
  ElMessage.info('代码已重置')
}

// 初始化加载模板
onMounted(() => {
  loadTemplate()
})
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
  background-clip: text;
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
