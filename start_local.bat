@echo off
echo RandomAnalysis Sunucusu Baslatiliyor...
:: Sanal ortami aktif et
call venv\Scripts\activate
:: FastAPI sunucusunu baslat (app.py dosyasini referans alir)
uvicorn app:app --reload
pause