import binascii
import time
import jwt
from ecdsa import SigningKey, SECP256k1
from src.storage.config import ORG_DID,ORG_SECRET_KEY

def generate_jwt(node_did):
    secret_key = bytes(ORG_SECRET_KEY, 'utf-8')
    secret_key=binascii.unhexlify(secret_key)
    signer = SigningKey.from_string(secret_key, curve=SECP256k1)
    
    payload = {
        "iss": ORG_DID,
        "aud": node_did,
        "exp": int(time.time()) + 3600
    }
    print("Jwttttt")
    return jwt.encode(payload, signer.to_pem(), algorithm="ES256K")

