@echo off
cls
:: take 2 arguments: game and file
if "%~2"=="" (
    echo Usage: .\%~nx0 ^<game^> ^<file^>
    exit /b 1
)
set "game_fullpath=%~f1"
set "game_name=%~nx1"
set "game_dir=%~dp1"
set "game_title=%~n1"

set "file_fullpath=%~f2"
set "file_name=%~nx2"
set "file_dir=%~dp2"
set "file_title=%~n2"

echo syncing %game_name% and %file_name% ...
timeout /t 1 /nobreak >nul 2>&1

:: create sync.bat 
echo @echo off > "%game_dir%sync.bat"
;(
    ;(echo(start "" "%game_fullpath%")
    ;(echo(start "" "%file_fullpath%")
    ;(echo(timeout /t 30)
    ;(echo(^:check)
    ;(echo(timeout /t 10 /nobreak ^>nul 2^>^&1)
    ;(echo(tasklist /NH /FI ^"IMAGENAME eq %game_name%^" 2^>nul ^| find /I /N ^"%game_name%^"^>nul)
    ;(echo(if not ^"%%ERRORLEVEL%%^"^=^=^"1^" goto check)
    ;(echo(.)
    ;(echo(timeout /t 10 /nobreak ^>nul 2^>^&1)
    ;(echo(taskkill /im ^"%file_name%^" /f)
    ;(echo(.)
    ;(echo(pause)
    
;) >> "%game_dir%sync.bat"

echo CreateObject("Wscript.Shell").Run "sync.bat", 0, True > "%game_dir%sync.vbs"

echo rm "%game_dir%sync.bat" > uninstall\%game_title%_%file_title%.bat
echo rm "%game_dir%sync.vbs" >> uninstall\%game_title%_%file_title%.bat
echo rm "%%~f0" >> uninstall\%game_title%_%file_title%.bat

iexpress /n /q /m "%game_dir%sync.bat"
echo. 
echo sync.bat and sync.vbs were successfully created in %game_dir%

exit /b 0
