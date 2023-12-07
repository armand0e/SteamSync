@echo off
:: take 2 arguments: game and app
if "%~2"=="" (
    echo Usage: %~nx0 ^<game^> ^<app^>
    pause
    exit /b 1
)
set "game_fullpath=%~f1"
set "game_name=%~nx1"
set "game_dir=%~dp1"

set "app_fullpath=%~f2"
set "app_name=%~nx2"
set "app_dir=%~dp2"

echo            Syncing %game_name% and %app_name% ...
pause

:: create sync.bat 
echo            Creating sync.bat in %game_dir% ...
;(
    ;(echo(@echo off)
    ;(echo(start "" "%game_fullpath%")
    ;(echo(start "" "%app_fullpath%")
    ;(echo(timeout /t 30)
    ;(echo(^:check)
    ;(echo(timeout /t 10 /nobreak ^>nul 2^>^&1)
    ;(echo(tasklist /NH /FI ^"IMAGENAME eq %game_name%^" 2^>nul ^| find /I /N ^"%game_name%^"^>nul)
    ;(echo(if not ^"%%ERRORLEVEL%%^"^=^=^"1^" goto check)
    ;(echo(.)
    ;(echo(timeout /t 10 /nobreak ^>nul 2^>^&1)
    ;(echo(taskkill /im ^"%app_name%^" /f)
    ;(echo(.)
    ;(echo(pause)
    
;) >> "%game_dir%/sync.bat"

echo CreateObject("Wscript.Shell").Run "sync.bat", 0, True > "%game_dir%/sync.vbs"
iexpress /n /q /m "%game_dir%/sync.bat"
exit /b 0
