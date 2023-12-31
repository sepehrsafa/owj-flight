@echo off
start cmd /k "cd E:\dev\owjcrs-project\microservices\flight && venv\Scripts\activate && celery -A app worker --loglevel=INFO --pool=solo -Q search_queue"