import asyncio
from typing import Dict, List
from fastapi import HTTPException


class Pool:
    pool_id: int
    pool_values: List[float]

    def __init__(self, pool_id: int, pool_value: List[float]):
        self.pool_id = pool_id
        self.pool_value = pool_value


class PoolManager:
    _instance = None  # Singleton instance
    _lock = asyncio.Lock()  # Async lock to avoid race condition
    pools: Dict[int, Pool] = {}

    def __new__(cls):
        """Ensure a single instance of PoolManager (Singleton)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.pools = {}  # Initialize the pool dictionary
        return cls._instance

    async def get_pools(self) -> Dict[int, Pool]:
        """Return the dictionary containing all pools."""
        return self.pools

    async def is_exists(self, pool_id: int) -> bool:
        """Check if a pool exists."""
        return pool_id in self.pools

    async def add_pool(self, pool_id: int,
                       pool_value: List[float]):
        """Add a new pool or update an existing pool"""
        if (
            not isinstance(pool_value, list) or
            not all(isinstance(v, (int, float)) for v in pool_value)
        ):
            raise HTTPException(status_code=400,
                                detail="pool_value must be a list of numbers")

        async with self._lock:
            if pool_id in self.pools:
                self.pools[pool_id].pool_value.extend(pool_value)
                return "Appended"
            else:
                self.pools[pool_id] = Pool(pool_id, pool_value)
                return "Inserted"

    async def update_pools(self, new_data: Dict[int, Pool]):
        """Replace all pools with new data."""
        async with self._lock:
            self.pools.clear()
            self.pools.update(new_data)

    async def query_pool(self, pool_id: int):
        """Return values of a pool."""
        if not await self.is_exists(pool_id):
            raise HTTPException(status_code=404,
                                detail="Pool not found")
        return self.pools[pool_id]

    async def cal_quantile(self, pool_id: int, k: int):
        """
        Calculates the k-th percentile of a list of numerical values.

        Args:
            pool_id (int): ID of the pool.
            k (int): The percentile to calculate (0-100).

        Returns:
            float: The calculated k-th percentile.

        Raises:
            HTTPException: If k is not between 0 and 100,
            or if pool does not exist.
        """
        if not self.is_exists(pool_id):
            raise HTTPException(status_code=404,
                                detail="Pool not found")

        if k > 100:
            raise HTTPException(
                status_code=400,
                detail="Percentile k must be between 0 and 100")

        x = sorted(self.pools[pool_id].pool_value)
        n = len(x)

        if n == 0:
            raise HTTPException(
                status_code=400,
                detail="Pool values must not be empty.")

        i = (k / 100) * (n - 1)
        j = int(i)

        if j + 1 >= n:
            return (x[j], n)
        return (x[j] + (i - j) * (x[j + 1] - x[j]), n)
