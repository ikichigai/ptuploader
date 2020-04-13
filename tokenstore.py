import redis
from datetime import timedelta
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD


def get_redis():
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=1,
        password=REDIS_PASSWORD
    )
    return r

def check_token(token):
    r = get_redis()

