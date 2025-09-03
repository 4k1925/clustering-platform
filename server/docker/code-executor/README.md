# 代码执行器 Docker 镜像

这个Docker镜像用于安全地执行学生提交的Python聚类算法代码。

## 功能特点

- 安全的沙箱环境
- 支持常见的数据科学库（NumPy, SciPy, scikit-learn, Matplotlib, Pandas）
- 资源限制（CPU和内存）
- 网络隔离
- 非root用户执行

## 构建镜像

### Windows系统 (PowerShell)

```powershell
# 在code-executor目录下执行
cd server/docker/code-executor
.\build.ps1
```

### Linux/Mac系统 (Bash)

```bash
# 在code-executor目录下执行
chmod +x build.sh
./build.sh
```

或者手动构建：

```bash
# 在code-executor目录下执行
docker build -t code-executor:latest .
```

## 安全策略

镜像包含安全策略文件`security.policy`，禁止以下危险操作：

- 系统操作（os, sys, subprocess）
- 文件操作（open, shutil）
- 网络操作（socket）
- 并发操作（threading, multiprocessing）
- 代码执行（eval, exec, compile）

## 使用方法

镜像已集成到平台的代码执行服务中，无需手动调用。

代码执行服务会：
1. 检查代码安全性
2. 创建临时执行环境
3. 在Docker容器中执行代码
4. 捕获输出和生成的图像
5. 返回执行结果

## 故障排除

如果遇到Docker相关问题：

1. 确保Docker服务正在运行
2. 检查用户权限（需要有Docker访问权限）
3. 查看Docker日志：`docker logs <container-id>`