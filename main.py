"""Main"""
from fastapi import FastAPI
import asyncio

from models.pool_models import PoolManager
from routers.pool_routes import router as pool_router
from utils.file_processors import load_binary_file, save_binary_file


app = FastAPI()
app.include_router(pool_router)
DATA_PATH = './data/output.pkl'
pool_manager = PoolManager()


async def periodic_save():
    pools_data = await pool_manager.get_pools()
    await save_binary_file(pools_data, DATA_PATH)


@app.on_event("startup")
async def startup_event():
    """
    This function is called when the application starts up.
    It loads data from a JSON file and updates the global `pools` variable.
    """
    print("App is starting...")
    x = await load_binary_file(DATA_PATH)
    await pool_manager.update_pools(x)
    asyncio.create_task(periodic_save())


@app.on_event("shutdown")
async def shutdown_event():
    """
    This function is called when the application shuts down.
    It saves data from the global `pools` variable to a JSON file.
    """
    pools = await pool_manager.get_pools()
    if pools:
        print("Saving pools data:", pools)
        await save_binary_file(pools, DATA_PATH)
    else:
        print("No data to save")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
