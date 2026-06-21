import redis
from dotenv import load_dotenv
import os

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)

r.set("name", "Siva")

value = r.get("name")

print("\nConnected Successfully!")
print("Redis Value:", value)