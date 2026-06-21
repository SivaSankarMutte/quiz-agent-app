import redis

from config.settings import settings


if settings.REDIS_URL:

    redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True
    )

else:

    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )