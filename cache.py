# Build a small FastAPI module that demonstrates a custom in-memory caching layer using dependency injection.

# Requirements:

# Create a Cache class that supports:
# get(key), set(key, value, ttl=None), and delete(key).
# TTL-based auto-expiry of items.
# Use this cache as a dependency injected into routes.
# Create a /products/{id} endpoint that:
# Returns cached data if available.
# If not, simulates fetching product details (with async sleep) and caches the result.
# Demonstrate cache invalidation via a /cache/clear endpoint.

from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Tuple

import asyncio
from fastapi import FastAPI, Depends

# -----------------------------
# Custom In-Memory Cache Layer
# -----------------------------


class Cache:
    """
    Simple in-memory cache with TTL support.

    - set(key, value, ttl=None): store value with optional TTL (in seconds)
    - get(key): return value if not expired, else None
    - delete(key): remove value from cache
    """

    def __init__(self):
        # key -> (value, expires_at: Optional[datetime])
        self._store: Dict[str, Tuple[Any, Optional[datetime]]] = {}

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at: Optional[datetime] = None
        if ttl is not None:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        self._store[key] = (value, expires_at)

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if not entry:
            return None

        value, expires_at = entry
        if expires_at is not None and datetime.utcnow() > expires_at:
            # Auto-delete expired item
            self.delete(key)
            return None

        return value

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


# Create a single cache instance for the app (in-memory, per-process)
cache_instance = Cache()


# Dependency injection wrapper
def get_cache() -> Cache:
    """
    FastAPI dependency that returns the shared cache instance.
    """
    return cache_instance


# -----------------------------
# FastAPI App & Endpoints
# -----------------------------

app = FastAPI(title="Cache Demo API")


# Simulate an async product fetch (e.g., from DB or external API)
async def fetch_product_from_source(product_id: int) -> dict:
    # Simulate network/database delay
    await asyncio.sleep(1)
    # Dummy product data
    return {
        "id": product_id,
        "name": f"Product {product_id}",
        "price": round(100 + product_id * 1.5, 2),
        "source": "database",  # mark that it came from the source, not cache
    }


@app.get("/products/{product_id}")
async def get_product(
    product_id: int,
    cache: Cache = Depends(get_cache),
):
    cache_key = f"product:{product_id}"

    # 1. Try cache
    cached = cache.get(cache_key)
    if cached is not None:
        # Mark that this came from cache just for demo purposes
        return {**cached, "from_cache": True}

    # 2. Simulate slow fetch
    product = await fetch_product_from_source(product_id)

    # 3. Store in cache with TTL (e.g., 30 seconds)
    cache.set(cache_key, product, ttl=30)

    return {**product, "from_cache": False}


@app.post("/cache/clear")
def clear_cache(cache: Cache = Depends(get_cache)):
    cache.clear()
    return {"detail": "Cache cleared"}

