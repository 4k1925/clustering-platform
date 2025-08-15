<template>
  <div class="code-debug-view">
    <div class="editor-container">
      <monaco-editor
        v-model="code"
        language="python"
        theme="vs-dark"
        :options="editorOptions"
      />
    </div>
    <div class="control-panel">
      <el-button type="primary" @click="runCode">运行</el-button>
      <el-button @click="resetCode">重置</el-button>
    </div>
    <div class="output-container">
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MonacoEditor from '@/components/editor/MonacoEditor.vue'
import { runClusterCode } from '@/api/clustering'

const code = ref(`# 输入你的聚类算法代码
from sklearn.cluster import KMeans
import numpy as np

# 示例数据
X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])

# 创建KMeans实例
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

# 输出结果
print("聚类标签:", kmeans.labels_)
print("聚类中心:", kmeans.cluster_centers_)`)

const output = ref('')
const editorOptions = {
  minimap: { enabled: false },
  fontSize: 14
}

const runCode = async () => {
  try {
    const res = await runClusterCode({ code: code.value })
    output.value = res.data.output
  } catch (error) {
    output.value = `Error: ${error.message}`
  }
}

const resetCode = () => {
  code.value = `# 输入你的聚类算法代码
from sklearn.cluster import KMeans
import numpy as np

# 示例数据
X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])

# 创建KMeans实例
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

# 输出结果
print("聚类标签:", kmeans.labels_)
print("聚类中心:", kmeans.cluster_centers_)`
  output.value = ''
}
</script>
