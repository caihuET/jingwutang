"""异常类定义"""


class AppException(Exception):
    """业务异常基类"""

    def __init__(self, code: int, message: str = None):
        self.code = code
        self.message = message or str(code)
        super().__init__(self.message)


class NotFoundError(AppException):
    """资源未找到"""

    def __init__(self, message: str = "资源未找到"):
        super().__init__(404, message)


class BadRequestError(AppException):
    """请求参数错误"""

    def __init__(self, message: str = "请求参数错误"):
        super().__init__(400, message)


class UnauthorizedError(AppException):
    """未授权"""

    def __init__(self, message: str = "未授权访问"):
        super().__init__(401, message)


class GameException(AppException):
    """游戏逻辑异常"""

    def __init__(self, code: int, message: str = None):
        super().__init__(code, message)
