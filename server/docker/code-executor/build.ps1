# PowerShell脚本，用于构建代码执行器Docker镜像

# 显示开始信息
Write-Host "开始构建代码执行器Docker镜像..." -ForegroundColor Green

# 获取脚本所在目录
$SCRIPT_DIR = $PSScriptRoot

# 构建Docker镜像
Write-Host "执行Docker构建命令..." -ForegroundColor Yellow
docker build -t code-executor:latest $SCRIPT_DIR

# 检查构建结果
if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker镜像构建成功: code-executor:latest" -ForegroundColor Green
} else {
    Write-Host "Docker镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host "完成" -ForegroundColor Green