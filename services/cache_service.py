import redis
from typing import Any, Optional

class CacheService:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Set a value in the cache with an expiration time."""
        self.redis_client.set(key, value, ex=expire)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        return self.redis_client.get(key)

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        self.redis_client.delete(key)

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return self.redis_client.exists(key)

# Example usage
if __name__ == "__main__":
    cache = CacheService()
    cache.set("example_key", "example_value", 3600)
    print(cache.get("example_key"))
