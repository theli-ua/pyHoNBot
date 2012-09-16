@echo off
MODE CON: COLS=150 LINES=500

:START
echo honbot starting
D:\python27\python.exe honbot
echo honbot exited, restarting
GOTO START
@echo on
