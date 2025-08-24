# server/app/models/__init__.py
from datetime import datetime
import json

class SerializerMixin:
    """通用序列化混入类"""
    
    def to_dict(self, exclude=None, include_relationships=False, depth=1):

        result = {}
        exclude = exclude or []
        
        # 序列化基本字段
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
                
            value = getattr(self, column.name)
            
            # 处理特殊数据类型
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, (dict, list)) and column.type.python_type in (dict, list):
                # 处理JSON字段
                value = json.loads(json.dumps(value, default=str))
                
            result[column.name] = value
        
        # 序列化关联对象（有限深度）
        if include_relationships and depth > 0:
            for rel_name, relationship in self.__mapper__.relationships.items():
                if rel_name in exclude:
                    continue
                    
                rel_value = getattr(self, rel_name)
                if rel_value is None:
                    result[rel_name] = None
                elif hasattr(rel_value, 'to_dict'):
                    # 单个关联对象
                    result[rel_name] = rel_value.to_dict(
                        exclude=exclude, 
                        include_relationships=True, 
                        depth=depth-1
                    )
                elif hasattr(rel_value, '__iter__'):
                    # 多个关联对象
                    result[rel_name] = [
                        item.to_dict(
                            exclude=exclude, 
                            include_relationships=True, 
                            depth=depth-1
                        ) for item in rel_value if hasattr(item, 'to_dict')
                    ]
        
        return result
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建对象实例"""
        instance = cls()
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance