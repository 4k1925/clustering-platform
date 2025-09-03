import docker
import redis
import json
import tempfile
import os
import uuid
import time
from datetime import datetime, timedelta

class CodeExecutor:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        # 创建安全的Docker镜像
        self._build_safe_image()
    
    def _build_safe_image(self):
        """构建安全的Python执行环境镜像"""
        try:
            # 检查镜像是否存在
            self.docker_client.images.get('code-executor:latest')
            print("代码执行器Docker镜像已存在")
        except Exception as e:
            # 处理镜像不存在的情况
            if "No such image" in str(e):
                print("代码执行器Docker镜像不存在，尝试构建...")
            
            # 获取Docker目录路径 - 使用正斜杠以兼容不同操作系统
            current_file = os.path.abspath(__file__)
            app_dir = os.path.dirname(os.path.dirname(current_file))
            server_dir = os.path.dirname(app_dir)
            docker_dir = os.path.join(server_dir, 'docker', 'code-executor')
            docker_dir = docker_dir.replace('\\', '/')  # 确保路径格式一致
            
            if os.path.exists(docker_dir):
                try:
                    # 使用预定义的Dockerfile构建镜像
                    self.docker_client.images.build(
                        path=docker_dir,
                        tag='code-executor:latest',
                        rm=True
                    )
                    print("代码执行器Docker镜像构建成功")
                except Exception as e:
                    print(f"构建Docker镜像失败: {str(e)}")
                    print(f"请尝试手动构建: cd {docker_dir} && docker build -t code-executor:latest .")
            else:
                print(f"Docker目录不存在: {docker_dir}")
                print("请确保Docker目录结构正确")

    def _create_safe_environment(self, code):
        """创建安全的执行环境"""
        # 安全检查
        dangerous_patterns = [
            'import os', 'import sys', 'subprocess', 'eval(', 'exec(',
            'open(', 'write(', 'delete', 'remove', 'shutil', '__import__',
            'socket', 'threading', 'multiprocessing', 'compile('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code.lower():
                raise SecurityError(f'检测到危险操作: {pattern}')

        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        code_file = os.path.join(temp_dir, 'main.py')
        
        # 写入代码文件
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write('''# 安全执行环境
import os
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.datasets import make_blobs, make_moons
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
import matplotlib
# 确保matplotlib使用正确的缓存目录
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
os.environ['TMPDIR'] = '/tmp'
os.makedirs('/tmp/matplotlib', exist_ok=True)
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import io
import base64
import json
import tempfile
 # 设置临时目录
tempfile.tempdir = '/tmp'             
# 重定向标准输出
import sys
from contextlib import redirect_stdout, redirect_stderr

output_buffer = io.StringIO()
error_buffer = io.StringIO()

try:
    with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
''')
            # 添加用户代码（每行缩进8个空格）
            for line in code.split('\n'):
                f.write(' ' * 8 + line + '\n')
            
            f.write('''
        # 捕获所有图像并转换为base64
        images = []
        for i, fig in enumerate(plt.get_fignums()):
            img_buffer = io.BytesIO()
            plt.figure(fig)
            plt.savefig(img_buffer, format='png', bbox_inches='tight')
            img_buffer.seek(0)
            images.append({
                'id': i,
                'data': base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            })
            plt.close(fig)
        
        result = {
            'output': output_buffer.getvalue(),
            'error': error_buffer.getvalue(),
            'images': images,
            'success': True
        }
        
except Exception as e:
    result = {
        'output': output_buffer.getvalue(),
        'error': f"执行错误: {str(e)}",
        'images': [],
        'success': False
    }

print(json.dumps(result))
''')

        return temp_dir, code_file

    def execute_code(self, code, algorithm='', timeout=30):
        """执行Python代码"""
        temp_dir = None
        try:
            # 创建安全环境
            temp_dir, code_file = self._create_safe_environment(code)
            
            # 在Windows上转换路径格式
            docker_temp_dir = temp_dir
            if os.name == 'nt':
                # 将Windows路径转换为Docker可用的格式
                temp_dir_abs = os.path.abspath(temp_dir)
                docker_temp_dir = temp_dir_abs.replace('\\', '/')
                if ':' in docker_temp_dir:
                    drive_letter = docker_temp_dir[0].lower()
                    docker_temp_dir = f'/{drive_letter}' + docker_temp_dir[2:]
            
            print(f"execute_code - 主机路径: {temp_dir}")
            print(f"execute_code - Docker路径: {docker_temp_dir}")
            
            # 执行Docker容器
            container = self.docker_client.containers.run(
                image='code-executor:latest',
                command=f'python /app/main.py',
                volumes={
                    docker_temp_dir: {'bind': '/app', 'mode': 'ro'}
                },
                mem_limit='256m',
                cpu_period=100000,
                cpu_quota=50000,
                network_mode='none',
                read_only=True,
                tmpfs={
                    '/tmp': 'rw,exec,size=64M',
                    '/var/tmp': 'rw,exec,size=32M'
                },
                remove=True,
                stdout=True,
                stderr=True,
                detach=False
            )
            
            # 获取容器输出
            container_output = container.decode('utf-8') if container else ''
            print(f"execute_code - 容器原始输出: {repr(container_output)}")
            print(f"execute_code - 容器输出长度: {len(container_output)}")
            
            # 解析结果 - 使用更健壮的方法
            result = {}
            try:
                if container_output.strip():
                    # 尝试从输出中提取JSON
                    json_start = container_output.find('{')
                    json_end = container_output.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = container_output[json_start:json_end]
                        result = json.loads(json_str)
                    else:
                        # 如果没有找到JSON，可能是纯文本输出
                        result = {
                            'output': container_output,
                            'error': '',
                            'images': [],
                            'success': False
                        }
                else:
                    result = {
                        'output': '',
                        'error': '容器执行成功但没有输出',
                        'images': [],
                        'success': False
                    }
                    
            except json.JSONDecodeError as e:
                print(f"execute_code - JSON解析失败: {str(e)}")
                result = {
                    'output': container_output,
                    'error': f'输出格式错误: {str(e)}',
                    'images': [],
                    'success': False
                }
            
            return result
            
        except docker.errors.ContainerError as e:
            error_msg = f'容器执行错误: {str(e)}'
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f"\nStderr: {e.stderr.decode('utf-8')}"
            print(f"execute_code - {error_msg}")
            return {
                'output': '',
                'error': error_msg,
                'images': [],
                'success': False
            }
            
        except Exception as e:
            error_msg = f'系统错误: {str(e)}'
            print(f"execute_code - {error_msg}")
            return {
                'output': '',
                'error': error_msg,
                'images': [],
                'success': False
            }
            
        finally:
            # 确保清理临时目录
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    print(f"execute_code - 清理临时目录失败: {str(e)}")    
                   

            
        
class SecurityError(Exception):
    pass

# 全局执行器实例
code_executor = CodeExecutor()
executor = code_executor