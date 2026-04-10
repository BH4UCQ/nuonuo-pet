"""
自定义异常类
"""


class NuonuoPetException(Exception):
    """基础异常类"""
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class AllModelsUnavailableError(NuonuoPetException):
    """所有模型不可用异常"""
    def __init__(self, message: str = "All AI models are unavailable"):
        super().__init__(message)


class ModelNotFoundError(NuonuoPetException):
    """模型未找到异常"""
    def __init__(self, model_name: str):
        super().__init__(f"Model '{model_name}' not found")


class DeviceNotFoundError(NuonuoPetException):
    """设备未找到异常"""
    def __init__(self, device_id: str):
        super().__init__(f"Device '{device_id}' not found")


class PetNotFoundError(NuonuoPetException):
    """宠物未找到异常"""
    def __init__(self, pet_id: int):
        super().__init__(f"Pet '{pet_id}' not found")


class AuthenticationError(NuonuoPetException):
    """认证失败异常"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class AuthorizationError(NuonuoPetException):
    """授权失败异常"""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message)


class ValidationError(NuonuoPetException):
    """验证失败异常"""
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class ResourceNotFoundError(NuonuoPetException):
    """资源未找到异常"""
    def __init__(self, resource_id: int):
        super().__init__(f"Resource '{resource_id}' not found")


class SyncConflictError(NuonuoPetException):
    """同步冲突异常"""
    def __init__(self, message: str = "Sync conflict detected"):
        super().__init__(message)


class OfflineModeError(NuonuoPetException):
    """离线模式异常"""
    def __init__(self, message: str = "Operation not available in offline mode"):
        super().__init__(message)
