@echo off

set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%..\..\"

if not exist "%ROOT_DIR%.venv" (
    echo error: virtual environment not found 1>&2
    echo run setup first 1>&2
    exit /b 1
)

call "%ROOT_DIR%.venv\Scripts\activate.bat"

set "PYTHONPATH=%ROOT_DIR%src"

python "%SCRIPT_DIR%grade.py" %*
