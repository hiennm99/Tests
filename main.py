from fastapi import FastAPI
from models.data_models import PickleShardManager
from routers.pool_routes import router as pool_router

app = FastAPI()
pool_manager = PickleShardManager(num_shards=3)
app.include_router(pool_router)

@app.on_event("startup")
async def startup_event():
    print("App is starting...")

@app.on_event("shutdown")
async def shutdown_event():
    print("App is shutting down...")
