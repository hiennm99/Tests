from fastapi import APIRouter, Depends, HTTPException
from schemas.pool_schemas import PoolInput, PoolQuery
from models.data_models import PickleShardManager
from utils.calculators import cal_percentile


router = APIRouter(
    prefix="/api/v1/pool",
    tags=["pool"],
)

def get_pool_manager() -> PickleShardManager:
    """Dependency to get instance of PickleShardManager"""
    from main import pool_manager
    return pool_manager

@router.post("/add")
async def add_pool(
    payload: PoolInput,
    pool_manager: PickleShardManager = Depends(get_pool_manager),
):
    """Insert or update record"""
    if not pool_manager.exists(payload.poolId):
        status = pool_manager.insert(payload.poolId, payload.poolValues)
    else:
        status = pool_manager.update(payload.poolId, payload.poolValues)

    return {"status": status}

@router.post("/calculate/percentile")
async def cal_percentile_route(
    payload: PoolQuery,
    pool_manager: PickleShardManager = Depends(get_pool_manager)
):
    """Calculate percentile"""
    values = pool_manager.find_by_key(payload.poolId)
    percentile, count = cal_percentile(values, payload.percentile)
    
    return {
        "percentile": percentile,
        "count": count
    }