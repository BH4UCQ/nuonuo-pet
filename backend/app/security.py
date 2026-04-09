"""
安全管理模块
提供 API 密钥加密存储、验证等安全相关功能
"""
import os
import hashlib
import secrets
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecurityManager:
    """安全管理器，负责密钥加密、解密等安全操作"""

    def __init__(self, master_key: Optional[str] = None):
        """
        初始化安全管理器

        Args:
            master_key: 主密钥，如果不提供则从环境变量读取
        """
        self.master_key = master_key or os.getenv("NUONUO_MASTER_KEY")
        if not self.master_key:
            # 如果没有主密钥，生成一个临时密钥（仅用于开发环境）
            self.master_key = self._generate_temp_master_key()

        self._fernet = self._create_fernet()

    def _generate_temp_master_key(self) -> str:
        """生成临时主密钥（仅用于开发环境）"""
        # 在生产环境中应该从安全的地方获取
        return secrets.token_urlsafe(32)

    def _create_fernet(self) -> Fernet:
        """创建 Fernet 加密器"""
        # 使用 PBKDF2 从主密钥派生加密密钥
        salt = b'nuonuo-pet-salt'  # 固定盐值（生产环境应该使用随机盐）
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return Fernet(key)

    def encrypt_api_key(self, api_key: str) -> str:
        """
        加密 API 密钥

        Args:
            api_key: 原始 API 密钥

        Returns:
            加密后的密钥（Base64 编码）
        """
        if not api_key:
            return ""

        encrypted = self._fernet.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """
        解密 API 密钥

        Args:
            encrypted_key: 加密后的密钥

        Returns:
            原始 API 密钥
        """
        if not encrypted_key:
            return ""

        try:
            encrypted = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt API key: {e}")

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        哈希密码

        Args:
            password: 原始密码
            salt: 盐值，如果不提供则生成新的

        Returns:
            (哈希值, 盐值)
        """
        if not salt:
            salt = secrets.token_urlsafe(16)

        # 使用 SHA256 哈希
        hash_value = hashlib.sha256((password + salt).encode()).hexdigest()
        return hash_value, salt

    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """
        验证密码

        Args:
            password: 待验证的密码
            hash_value: 存储的哈希值
            salt: 盐值

        Returns:
            是否匹配
        """
        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hash_value)

    def generate_token(self, length: int = 32) -> str:
        """
        生成随机令牌

        Args:
            length: 令牌长度

        Returns:
            随机令牌
        """
        return secrets.token_urlsafe(length)

    def validate_api_key_format(self, api_key: str, provider: str) -> bool:
        """
        验证 API 密钥格式

        Args:
            api_key: API 密钥
            provider: 提供商名称

        Returns:
            是否有效
        """
        if not api_key:
            return False

        # 根据不同提供商验证格式
        if provider == "openai":
            # OpenAI API key 通常以 sk- 开头
            return api_key.startswith("sk-") and len(api_key) >= 20
        elif provider == "anthropic":
            # Anthropic API key 格式验证
            return len(api_key) >= 20
        else:
            # 其他提供商，基本长度检查
            return len(api_key) >= 10

    def mask_api_key(self, api_key: str, visible_chars: int = 4) -> str:
        """
        遮蔽 API 密钥，只显示部分字符

        Args:
            api_key: API 密钥
            visible_chars: 可见字符数

        Returns:
            遮蔽后的密钥
        """
        if not api_key or len(api_key) <= visible_chars * 2:
            return "***"

        return f"{api_key[:visible_chars]}...{api_key[-visible_chars:]}"


# 全局安全管理器实例
_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """获取安全管理器实例"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


def encrypt_api_key(api_key: str) -> str:
    """加密 API 密钥（便捷函数）"""
    return get_security_manager().encrypt_api_key(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API 密钥（便捷函数）"""
    return get_security_manager().decrypt_api_key(encrypted_key)


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """遮蔽 API 密钥（便捷函数）"""
    return get_security_manager().mask_api_key(api_key, visible_chars)
