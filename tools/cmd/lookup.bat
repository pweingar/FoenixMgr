@echo off
REM Print the contents of memory at the labeled address
REM usage: lookup {label}

if [%2%]==[] (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --lookup %1
) ELSE (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --lookup %1 --count %2
)
