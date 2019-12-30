@echo off
REM Upload a binary file to the C256 Foenix

if [%2%]==[] (
    python C256Mgr\c256mgr.py --binary %1
) ELSE (
    python C256Mgr\c256mgr.py --binary %1 --address %2
)