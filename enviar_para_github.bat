@echo off
title Enviar alterações para o GitHub
cls
echo ============================================================
echo         ENVIANDO PROJETO PARA O GITHUB (RAILWAY)
echo ============================================================
echo.
.\mingit\cmd\git.exe push -u origin main --force
echo.
echo ============================================================
echo Finalizado! A Railway atualizará automaticamente em 1 minuto.
echo ============================================================
pause
