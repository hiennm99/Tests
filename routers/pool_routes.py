"""Declare route for pool

This module provides API routes for managing pool data,
including adding new records and querying quantiles.
"""
from fastapi import APIRouter

from schemas.pool_schemas import PoolInput, PoolQuery
from models.pool_models import PoolManager

router = APIRouter(
    prefix="/api/v1/pool",
    tags=["pool"],
)
pool_manager = PoolManager()


@router.post("/add")
async def add_pool(data: PoolInput):
    """Insert new record or Update existed record

    Args:
        data (PoolInput): The input data containing poolId and poolValues.
        pools (dict): The current pools data.

    Returns:
        dict: A dictionary containing the status of the operation.
    """
    status = await pool_manager.add_pool(data.poolId, data.poolValues)

    return {
        "status": status
    }


@router.post("/calculate/quantile")
async def query_quantile(data: PoolQuery):
    """Calculate quantile & count if record is exist

    Args:
        data (PoolQuery): The input data containing poolId and percentile.
        pools (dict): The current pools data.

    Returns:
        dict: A dictionary containing the quantile value and count of values.
    """
    quantile, count = await pool_manager.cal_quantile(data.poolId,
                                                      data.percentile)

    return {
        "quantile": quantile,
        "count": count
    }
