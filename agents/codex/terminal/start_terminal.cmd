@echo off
cd /d "%~dp0"
if defined THEBEGINNING_PYTHON (
  "%THEBEGINNING_PYTHON%" server.py --open
) else (
  py -3 server.py --open
)
pause
