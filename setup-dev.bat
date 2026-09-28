@echo off
setlocal

rem setup-dev.bat があるディレクトリへ移動
cd /d "%~dp0"

python -m venv .venv-dev
call .venv-dev\Scripts\activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt

echo Setup completed.
