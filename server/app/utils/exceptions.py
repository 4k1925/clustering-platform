class NotFoundException(Exception):
    """资源未找到异常"""
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(Exception):
    """未授权异常"""
    def __init__(self, message="Unauthorized"):
        self.message = message
        super().__init__(self.message)

class ValidationException(Exception):
    """验证异常"""
    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)