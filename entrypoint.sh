#!/bin/bash

gunicorn --pythonpath /src -b 0.0.0.0:$SERVICE_PORT --workers=1 -k sync -t $SERVICE_TIMEOUT recommendation_service:app
