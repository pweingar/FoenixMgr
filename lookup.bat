@echo off
REM Print the contents of memory at the labeled address
REM usage: lookup {label}

if [%2%]==[] (
    python C256Mgr\c256mgr.py --lookup %1
) ELSE (
    python C256Mgr\c256mgr.py --lookup %1 --count %2
)