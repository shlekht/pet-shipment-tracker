from celery import Celery

from shipment_tracking_api.config import settings

celery = Celery(
    main=__name__,
    broker=settings.BROKER_REDIS_URL,
    include=["shipment_tracking_api.infrastructure.tasks.tasks"]
)

