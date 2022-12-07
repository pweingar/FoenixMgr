@echo off
rem Bundle up the python scripts into a ZIP file for easier use

cd FoenixMgr
copy /y fnxmgr.py __main__.py
zip FoenixMgr.zip *.py
cd ..
copy /y FoenixMgr\FoenixMgr.zip FoenixMgr.zip
del FoenixMgr\FoenixMgr.zip
del FoenixMgr\__main__.py