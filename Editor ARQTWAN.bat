@echo off
title Editor ARQTWAN
cd /d "%~dp0"
echo.
echo  Abriendo el editor de ARQTWAN...
echo  (No cierres esta ventana mientras editas)
echo.
python tools\editor.py
if errorlevel 1 (
  echo.
  echo  No se pudo iniciar el editor.
  echo  Comprueba que Python esta instalado:  python --version
  echo.
  pause
)
