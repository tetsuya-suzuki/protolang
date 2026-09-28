@echo off
setlocal

rem このバッチファイルが置かれているディレクトリ
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%.venv" (
    echo error: virtual environment not found 1>&2
    echo run setup.bat first 1>&2
    exit /b 1
)

call "%SCRIPT_DIR%.venv\Scripts\activate"

set "PYTHONPATH=%SCRIPT_DIR%src"

python -m protolang.main %*
