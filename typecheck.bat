@echo off
setlocal

rem このバッチファイルが置かれているディレクトリ
set "SCRIPT_DIR=%~dp0"

if not exist "%SCRIPT_DIR%.venv-dev" (
    echo error: virtual environment not found 1>&2
    echo run setup-dev.bat first 1>&2
    exit /b 1
)

call "%SCRIPT_DIR%.venv-dev\Scripts\activate"

cd /d "%SCRIPT_DIR%"
python -m mypy src
