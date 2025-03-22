#!/bin/bash
set -ex
sleep 5
alembic revision --autogenerate -m "Init migration"
alembic upgrade head
uvicorn main:app --log-level=debug --host=0.0.0.0 --port=5000
