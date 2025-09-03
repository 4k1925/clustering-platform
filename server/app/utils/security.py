def validate_python_code(code: str) -> tuple:
    """深度验证Python代码安全性"""
    # 语法检查
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        return False, f"语法错误: {str(e)}"
    
    # 抽象语法树分析
    try:
        import ast
        tree = ast.parse(code)
        
        # 检查危险的AST节点
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ['os', 'sys', 'subprocess']:
                        return False, f"禁止导入: {alias.name}"
            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'open']:
                        return False, f"禁止调用: {node.func.id}"
    
    except Exception as e:
        return False, f"代码分析错误: {str(e)}"
    
    return True, "代码验证通过"