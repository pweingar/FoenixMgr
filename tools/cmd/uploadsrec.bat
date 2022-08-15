@echo off
REM Upload an SREC file to the Foenix

python %FOENIXMGR%\FoenixMgr\fnxmgr.py --upload-srec %1
