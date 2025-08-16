import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './api'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from './utils/axios'

const app = createApp(App)
const pinia = createPinia()


app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 全局挂载axios
app.config.globalProperties.$axios = axios

app.mount('#app')
