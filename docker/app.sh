#!/bin/bash

alembic upgrade head

gunicorn src.shipment_tracking_api.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 