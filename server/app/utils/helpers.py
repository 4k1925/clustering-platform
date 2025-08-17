from datetime import datetime
import os
def format_date(date_value, format_str="%Y-%m-%d %H:%M"):
    """格式化日期"""
    if not date_value:
        return ""
    if isinstance(date_value, str):
        return date_value
    return date_value.strftime(format_str)

def to_dict(model_instance):
    """将模型实例转换为字典"""
    if not model_instance:
        return None
    return {c.name: getattr(model_instance, c.name) for c in model_instance.__table__.columns}


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def ensure_upload_folder(app):
    """确保上传文件夹存在"""
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)