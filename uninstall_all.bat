for /f "tokens=*" %%a in ('dir /b /s /a:-d "uninstall\*.bat"') do (
    echo uninstalling %%a ...
    call %%a
)
