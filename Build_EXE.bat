@echo off
title Building Zabbatha Standalone EXE
echo =======================================================
echo   Zabbatha (ظبطها) - Autonomous Game Optimizer Pro
echo   Packaging into Single Standalone Windows Executable (.exe)
echo =======================================================
echo.

python -m PyInstaller --noconfirm --onefile --windowed --name "Zabbatha" --clean run.py

echo.
if exist "dist\Zabbatha.exe" (
    echo [SUCCESS] Zabbatha.exe built successfully in dist\Zabbatha.exe!
) else (
    echo [ERROR] Build encountered an issue. Check the output above.
)
echo.
pause
