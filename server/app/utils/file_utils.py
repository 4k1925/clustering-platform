import os
import uuid
from werkzeug.utils import secure_filename

def save_file(file, upload_dir):
    """保存上传的文件并返回文件路径"""
    # 生成唯一文件名
    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    
    # 确保上传目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    return file_path

def get_file_size(file_path):
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)

def get_file_type(filename):
    """根据文件名获取文件类型"""
    ext = os.path.splitext(filename)[1].lower()
    
    # 常见文件类型映射
    type_map = {
        '.pdf': 'PDF',
        '.doc': 'Word',
        '.docx': 'Word',
        '.ppt': 'PowerPoint',
        '.pptx': 'PowerPoint',
        '.xls': 'Excel',
        '.xlsx': 'Excel',
        '.txt': 'Text',
        '.zip': 'Archive',
        '.rar': 'Archive',
        '.jpg': 'Image',
        '.jpeg': 'Image',
        '.png': 'Image',
        '.mp4': 'Video',
        '.avi': 'Video',
        '.mov': 'Video',
    }
    
    return type_map.get(ext, 'Other')