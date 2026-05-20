@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo 正在建立虛擬環境並安裝依賴...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
)
.venv\Scripts\python.exe main.py
pause
