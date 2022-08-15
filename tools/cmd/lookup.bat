@echo off
REM Print the contents of memory at the labeled address
REM usage: lookup {label}

if [%2%]==[] (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --lookup %1
) ELSE (
    python %FOENIXHOME%\FoenixMgr\fnxmgr.py --lookup %1 --count %2
)
