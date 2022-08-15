@echo off
REM Print the contents of memory, given the label of a pointer to the start address
REM usage: deref {label}
if [%2%]==[] (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --deref %1
) ELSE (
    python %FOENIXMGR%\FoenixMgr\fnxmgr.py --deref %1 --count %2
)
