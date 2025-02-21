@echo off

REM Get the directory of the script.
SET DIR=%~dp0

REM Remove the trailing backslash if it exists (Windows-specific).
IF "%DIR:~-1%" == "\" SET DIR=%DIR:~0,-1%

REM Create virtual environment and install requirements.
IF NOT EXIST "%DIR%\.venv" (
    python -m venv "%DIR%\.venv"
    CALL "%DIR%\.venv\Scripts\activate.bat"
    pip install -r "%DIR%\requirements.txt"
    CALL deactivate
)

REM Launch script in virtual environment.
CALL "%DIR%\.venv\Scripts\activate.bat"
python "%DIR%\PhoenixMgr\fnxmgr.py" %*
CALL deactivate

