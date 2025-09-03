#!/bin/bash

# 构建代码执行器Docker镜像
echo "开始构建代码执行器Docker镜像..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 构建Docker镜像
docker build -t code-executor:latest "$SCRIPT_DIR"

# 检查构建结果
if [ $? -eq 0 ]; then
    echo "Docker镜像构建成功: code-executor:latest"
else
    echo "Docker镜像构建失败"
    exit 1
fi

echo "完成"