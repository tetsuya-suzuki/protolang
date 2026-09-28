@echo off
setlocal

rem setup.bat があるディレクトリへ移動
cd /d "%~dp0"

if not exist ".venv" (
    echo error: virtual environment not found 1>&2
    echo run setup.bat first 1>&2
    exit /b 1
)

call .venv\Scripts\activate.bat

set PYTHONPATH=src

python tests\run_tests.py %*
