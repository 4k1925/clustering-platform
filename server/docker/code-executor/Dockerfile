FROM python:3.9-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 创建非root用户
RUN useradd -m -s /bin/bash coderunner

# 安装必要的包
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 创建临时目录并设置权限
RUN mkdir -p /tmp && chmod 777 /tmp
RUN mkdir -p /tmp/matplotlib && chmod 777 /tmp/matplotlib

# 设置目录权限
RUN chmod 755 /app

# 切换到非root用户
USER coderunner

# 安装Python依赖（使用更兼容的版本）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    numpy==1.21.0 \
    scipy==1.7.0 \
    scikit-learn==1.0.0 \
    matplotlib==3.4.0 \
    pandas==1.3.0

# 设置matplotlib缓存目录
RUN mkdir -p /home/coderunner/.cache/matplotlib && \
    chown coderunner:coderunner /home/coderunner/.cache/matplotlib && \
    chmod 777 /home/coderunner/.cache/matplotlib

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV MPLCONFIGDIR=/home/coderunner/.cache/matplotlib
ENV MATPLOTLIBRC=/home/coderunner/.cache/matplotlib