from celery import Celery

from shipment_tracking_api.config import settings

celery = Celery(
    main=__name__,
    broker=settings.RMQ_URL,
    include=["shipment_tracking_api.infrastructure.tasks.tasks"],
)
celery.conf.update(
    control_queue_exclusive=True,
    control_queue_durable=False,
    event_queue_exclusive=True,
    event_queue_durable=False,
)
