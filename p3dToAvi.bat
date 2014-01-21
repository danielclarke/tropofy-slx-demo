@echo off
call set PARENT_DIR=%CD%
set PARENT_DIR=%PARENT_DIR:\= %
set LAST_WORD=
for %%i in (%PARENT_DIR%) do set LAST_WORD=%%i

call set LAYOUT_FILE=%LAST_WORD%.lay
call set TRACE_FILE=%LAST_WORD%.atf
call set AVI_FILE=%LAST_WORD%.avi

start C:\Wolverine\P3D\sp3d.exe /MakeAVI 800 480 0 180 %LAYOUT_FILE% %TRACE_FILE% %AVI_FILE%