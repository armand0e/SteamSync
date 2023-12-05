@echo off

echo test > "%tmp%\test.txt"
copy "%tmp%\test.txt" "C:\Program Files (x86)\Steam\steamapps\common\test.txt"
cls
copy "%tmp%\test.txt" "C:\Program Files\Steam\steamapps\common\test.txt"
cls

set "steamapps="
if exist "C:\Program Files\Steam\steamapps\common\test.txt" (set "steamapps=Program Files\Steam\steamapps\common") 
if exist "C:\Program Files (x86)\Steam\steamapps\common\test.txt" (set "steamapps=Program Files (x86)\Steam\steamapps\common")

del "C:\Program Files (x86)\Steam\steamapps\common\test.txt""
del "C:\Program Files\Steam\steamapps\common\test.txt"
del "%tmp%\test.txt"
cls

echo Please select the target steamapp's executable file (usually .exe)
set ps_fn=ofd.ps1
echo [System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") ^| out-null > %ps_fn%
echo $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog >> %ps_fn%
echo $OpenFileDialog.initialDirectory = "C:\%steamapps%" >> %ps_fn%
echo $OpenFileDialog.ShowDialog() >> %ps_fn%
echo $OpenFileDialog.filename >> %ps_fn%
 
for /F "tokens=* usebackq" %%a in (`powershell -executionpolicy bypass -file %ps_fn%`) do if not "%%a" == "Cancel" if not "%%a" == "OK" set filename=%%a
del %ps_fn%
 
if not "%filename%"=="" echo %filename%
pause