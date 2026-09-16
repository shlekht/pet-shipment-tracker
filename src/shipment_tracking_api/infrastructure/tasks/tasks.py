from shipment_tracking_api.infrastructure.tasks.celery_app import celery


@celery.task
def some_task():
    pass # TODO