@echo off
REM Upload a binary file to the Foenix

if [%2%]==[] (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --upload %1
) ELSE (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --upload %1 --address %2
)
