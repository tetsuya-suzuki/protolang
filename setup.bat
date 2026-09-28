@echo off
setlocal

rem setup.bat があるディレクトリへ移動
cd /d "%~dp0"

python -m venv .venv
call .venv\Scripts\activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

echo Setup completed.
