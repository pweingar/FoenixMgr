@echo off
REM Reprogram the flash memory on the Foenix

if [%2%]==[] (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --flash %1
) ELSE (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --flash %1 --address %2
)
