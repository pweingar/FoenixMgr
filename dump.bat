@echo off
REM Print the contents of memory
REM usage: dump {start address} [{byte count}]

if [%2%]==[] (
    python C256Mgr\c256mgr.py --dump %1
) ELSE (
    python C256Mgr\c256mgr.py --dump %1 --count %2
)