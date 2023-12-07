@echo off
icacls * /reset /t /c /q 
cls

pip install -r requirements.txt
pip3 install -r requirements.txt
cls
echo. Setup complete! Press any key to exit.
timeout /t 10 >nul 2>&1