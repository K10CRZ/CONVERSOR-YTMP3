@echo off
title YTMP3 Pro - Conversor de YouTube para MP3
cls
echo ============================================================
echo           INICIANDO SERVIDOR DO CONVERSOR YTMP3
echo ============================================================
echo.
echo Abrindo a interface web no seu navegador...
echo Servidor rodando em: http://127.0.0.1:5000
echo.
echo Para fechar o programa, feche esta janela do Terminal.
echo.

start http://127.0.0.1:5000
python app.py
pause
