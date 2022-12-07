@echo off
REM Reprogram a flash sector on the Foenix

python %FOENIXMGR%\FoenixMgr\fnxmgr.py --flash-sector %1 --flash %2
