@echo off
REM Print the contents of memory, given the label of a pointer to the start address
REM usage: deref {label}
if [%2%]==[] (
    python C256Mgr\c256mgr.py --deref %1
) ELSE (
    python C256Mgr\c256mgr.py --deref %1 --count %2
)

