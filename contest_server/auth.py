import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get secrets from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "")  # Will be empty if not set
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
security = HTTPBearer()

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set. Please set it in .env file")

def create_token(name: str):
    payload = {
        "sub": name,
        "exp": time.time() + 86400
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")