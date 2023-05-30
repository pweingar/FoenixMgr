@echo off
REM Reprogram a flash sector on the Foenix

python %FOENIXMGR%\FoenixMgr\fnxmgr.py --target %1 --flash-sector %2 --flash %3
