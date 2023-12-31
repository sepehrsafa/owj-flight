@echo off
start cmd /k "cd E:\dev\owjcrs-project\microservices\flight && venv\Scripts\activate && uvicorn app.main:app --reload"