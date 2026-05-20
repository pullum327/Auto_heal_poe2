@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   POE2 Auto Flask - 打包程式
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] 建立虛擬環境...
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt -q
) else (
    echo [1/4] 使用現有虛擬環境
)

echo [2/4] 安裝 PyInstaller...
.venv\Scripts\pip install pyinstaller -q

echo [3/4] 開始打包（約 1~3 分鐘）...
.venv\Scripts\pyinstaller poe2_auto_flask.spec --noconfirm
if errorlevel 1 (
    echo.
    echo 打包失敗，請檢查上方錯誤訊息。
    pause
    exit /b 1
)

echo [4/4] 壓縮為 ZIP...
set OUT=dist\POE2_AutoFlask
set ZIP=dist\POE2_AutoFlask-Windows.zip
if exist "%ZIP%" del "%ZIP%"
powershell -NoProfile -Command "Compress-Archive -Path '%OUT%\*' -DestinationPath '%ZIP%' -Force"

echo.
echo ========================================
echo   完成！
echo ========================================
echo   資料夾: %OUT%
echo   執行檔: %OUT%\POE2_AutoFlask.exe
echo   壓縮包: %ZIP%
echo.
echo   上傳 %ZIP% 到 GitHub Releases 即可供人下載。
echo ========================================
pause
