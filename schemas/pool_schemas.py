"""
This module defines models used in the FastAPI application.

The models are built using Pydantic to ensure input data validation.
"""

from typing import List
from pydantic import BaseModel


class PoolInput(BaseModel):
    """
    The `PoolInput` model represents the input data for a pool.

    Attributes:
        poolId (int): The ID of the pool.
        poolValues (List[float]): A list of floating-point values for the pool.
    """
    poolId: int
    poolValues: List[float]


class PoolQuery(BaseModel):
    """
    The `PoolQuery` model is used for querying pool data.

    Attributes:
        poolId (int): The ID of the pool to query.
        percentile (float): The percentile value to retrieve.
    """
    poolId: int
    percentile: float
