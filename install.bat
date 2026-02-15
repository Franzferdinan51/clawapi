@echo off
REM ClawAPI Installer for Windows
REM Usage: install.bat

echo Installing ClawAPI for Windows...

REM Create virtual environment
python -m venv .venv
call .venv\Scripts\activate.bat

REM Install dependencies
pip install flask cryptography requests

REM Make CLI executable
icacls clawapi.py /grant Users:F

echo.
echo ========================================
echo   ClawAPI Windows Installation Complete!
echo ========================================
echo.
echo Usage:
echo   clawapi list                      - List providers
echo   clawapi add openai sk-xxx        - Add API key
echo   clawapi models openai            - List models
echo   clawapi set openai gpt-4o        - Set default model
echo   clawapi show openai              - Show masked key
echo   clawapi remove openai            - Remove provider
echo.
echo Web UI:
echo   .venv\Scripts\python.exe webui.py
echo   Then open http://localhost:5001
echo.

pause
