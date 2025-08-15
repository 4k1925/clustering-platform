<template>
  <div class="code-debug-view">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>代码编辑器</span>
              <el-button-group>
                <el-button type="primary" @click="runCode">运行</el-button>
                <el-button @click="resetCode">重置</el-button>
              </el-button-group>
            </div>
          </template>
          <monaco-editor
            v-model="code"
            language="python"
            theme="vs-dark"
            :options="editorOptions"
          />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>运行结果</span>
            </div>
          </template>
          <div class="output-container">
            <pre>{{ output }}</pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MonacoEditor from '@/components/editor/MonacoEditor.vue'
import { runClusterCode } from '@/api/clustering'

const code = ref(`# K-Means聚类示例
from sklearn.cluster import KMeans
import numpy as np

# 生成示例数据
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
    output.value = res.output || '代码执行成功，但没有输出'
  } catch (error) {
    output.value = `错误: ${error.message}`
  }
}

const resetCode = () => {
  code.value = `# K-Means聚类示例
from sklearn.cluster import KMeans
import numpy as np

# 生成示例数据
X = np.array([[1, 2], [1, 4], [1, 0], [4, 2], [4, 4], [4, 0]])

# 创建KMeans实例
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

# 输出结果
print("聚类标签:", kmeans.labels_)
print("聚类中心:", kmeans.cluster_centers_)`
  output.value = ''
}
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
.output-container {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  min-height: 300px;
  max-height: 500px;
  overflow: auto;
}
</style>
