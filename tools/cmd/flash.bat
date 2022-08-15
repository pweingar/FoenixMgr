@echo off
REM Reprogram the flash memory on the Foenix

if [%2%]==[] (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --flash %1
) ELSE (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --flash %1 --address %2
)
