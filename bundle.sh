# Bundle up the python scripts into a ZIP file for easier use

cd FoenixMgr
cp fnxmgr.py __main__.py
zip FoenixMgr.zip *.py
cd ..
cp FoenixMgr/FoenixMgr.zip FoenixMgr.zip
rm FoenixMgr/FoenixMgr.zip
rm FoenixMgr/__main__.py
