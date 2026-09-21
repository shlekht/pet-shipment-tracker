from contextlib import asynccontextmanager

from fastapi import FastAPI

from shipment_tracking_api.api.v1.auth import router as auth_router
from shipment_tracking_api.config import settings
from shipment_tracking_api.errors_handling.general_handler import (
    register_errors_handlers,
)
from shipment_tracking_api.infrastructure.cache.redis import RedisCacheBackend
from shipment_tracking_api.infrastructure.message_broker.rabbitmq import RabbitMQ


@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------------- Cache --------------
    cache_backend = RedisCacheBackend.from_url(
        redis_url=settings.REDIS_URL,
        cache_ttl_seconds=settings.CACHE_TTL_SECONDS,
    )
    await cache_backend.ping() 
    app.state.redis = cache_backend
    # ------------------------------------


    # -------- Message Broker ------------
    broker = RabbitMQ(url=settings.RMQ_URL)
    await broker.connect()
    app.state.rabbit = broker
    # ------------------------------------

    yield
    
    await cache_backend.close()
    await broker.close()

app = FastAPI(lifespan=lifespan)
register_errors_handlers(app)

app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}