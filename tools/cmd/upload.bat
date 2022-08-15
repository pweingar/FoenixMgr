@echo off
REM Upload a binary file to the Foenix

if [%2%]==[] (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --binary %1
) ELSE (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --binary %1 --address %2
)
