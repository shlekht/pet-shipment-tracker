#!/bin/bash

if [[ "${1}" == "celery" ]]; then
    celery --app=src.shipment_tracking_api.infrastructure.tasks.celery_app:celery worker -l INFO # TODO
elif [[ "${1}" == "flower" ]]; then
    celery --app=src.shipment_tracking_api.infrastructure.tasks.celery_app:celery flower # TODO
else
    echo "Unknown command: ${1}"
    exit 1
fi