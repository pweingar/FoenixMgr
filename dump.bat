@echo off
REM Print the contents of memory
REM usage: dump {start address} [{byte count}]

if [%2%]==[] (
    python C256Mgr\c256mgr.py -a %1%
) ELSE (
    python C256Mgr\c256mgr.py -a %1% -c %2%
)