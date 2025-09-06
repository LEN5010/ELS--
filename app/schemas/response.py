def success_response(data=None, message="Success"):
    """成功响应格式"""
    response = {
        "code": 200,
        "message": message,
        "data": data
    }
    return response

def error_response(message="Error", code=400):
    """错误响应格式"""
    response = {
        "code": code,
        "message": message,
        "data": None
    }
    return response, code