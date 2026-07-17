@echo off
title Function Generator Server
echo [1/2] Activating Virtual Environment...
call venv\Scripts\activate

echo [2/2] Starting FastAPI Server...
echo server is running at http://127.0.0.1:8000
uvicorn app:app --reload

pause