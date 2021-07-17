@echo off
REM Upload an SREC file to the C256 Foenix

python C256Mgr\c256mgr.py --upload-srec %1
