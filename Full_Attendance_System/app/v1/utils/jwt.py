import jwt
import os
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")

class JWTUtils:
    @staticmethod
    def generate_token(user_id: int, role: str, fingerprint: str, expires_in: int = 86400):  # Default: 1 day
        """
        Generate JWT token with user ID, role, and fingerprint.
        """
        payload = {
            "sub": user_id,
            "role": role,  # The user's role (admin, lecturer, student)
            "fingerprint": fingerprint,  # The user's fingerprint (or device fingerprint)
            "exp": datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str):
        """
        Verify the JWT token and return the user data.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return {
                "user_id": payload["sub"],
                "role": payload["role"],
                "fingerprint": payload["fingerprint"]
            }
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token
