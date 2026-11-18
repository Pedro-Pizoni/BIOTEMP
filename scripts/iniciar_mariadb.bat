@echo off
set MARIADB=%USERPROFILE%\Downloads\mariadb-10.6.28-winx64\mariadb-10.6.28-winx64

if not exist "%MARIADB%\bin\mariadbd.exe" (
  echo MariaDB nao encontrado em "%MARIADB%".
  pause
  exit /b 1
)
echo Iniciando MariaDB na porta 3306...
"%MARIADB%\bin\mariadbd.exe" --defaults-file="%MARIADB%\data\my.ini" --console
pause
