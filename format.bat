@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%.venv-dev" (
    echo error: virtual environment not found 1>&2
    echo run setup-dev first 1>&2
    exit /b 1
)

call "%SCRIPT_DIR%.venv-dev\Scripts\activate.bat"

cd /d "%SCRIPT_DIR%"
ruff format .
