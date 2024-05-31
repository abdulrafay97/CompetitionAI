# This file is responsible for signing , encoding , decoding and returning JWTS
import time
from typing import Dict

import jwt, os
# from decouple import config
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


JWT_SECRET = "CompitativeAI"
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_TIME_DAYS = 1


def token_response(token: str):
    return {
        "access_token": token
    }


# function used for signing the JWT string
def signJWT(user_id) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 36000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
