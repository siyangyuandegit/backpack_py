import base64
from config import api_secret
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# 生成私钥
private_key = ed25519.Ed25519PrivateKey.generate()

# 导出私钥
private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PrivateFormat.Raw,
    encryption_algorithm=serialization.NoEncryption()
)

# 获取公钥
public_key = private_key.public_key()

# 导出公钥
public_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
)

# 打印私钥和公钥（以字节形式）
print("Private Key:", private_bytes)
print("Public Key:", public_bytes)
print(base64.b64decode(api_secret))
