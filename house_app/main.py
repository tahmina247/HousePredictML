from fastapi import FastAPI
from house_app.api import house_model, auth
from house_app.db.database import SessionLocal
from fastapi_limiter import FastAPILimiter
import redis.asyncio as aioredis
from contextlib import asynccontextmanager
import uvicorn


async def init_redis():
    return await aioredis.from_url('redis://localhost', encoding='utf-8', decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await init_redis()
    await FastAPILimiter.init(redis_client)
    yield
    await redis_client.close()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


house_app = FastAPI(title='House Model', lifespan=lifespan)


house_app.include_router(auth.auth_router)
house_app.include_router(house_model.house_model_router)



if __name__ == "__main__":
    uvicorn.run(house_app, host="127.0.0.1", port=9000)