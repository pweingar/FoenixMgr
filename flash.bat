@echo off
REM Reprogram the flash memory on the C256 Foenix

if [%2%]==[] (
    python C256Mgr\c256mgr.py --flash %1
) ELSE (
    python C256Mgr\c256mgr.py --flash %1 --address %2
)