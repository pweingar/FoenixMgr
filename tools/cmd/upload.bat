@echo off
REM Upload a binary file to the Foenix

if [%2%]==[] (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --binary %1
) ELSE (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --binary %1 --address %2
)
