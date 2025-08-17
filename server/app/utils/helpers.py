from datetime import datetime

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