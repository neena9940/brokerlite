import redis
from app.core.config import settings

# decode_responses=True: get/set work with str, not bytes — fewer .decode() everywhere
redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)