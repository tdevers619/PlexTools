@echo off
setlocal enabledelayedexpansion

REM Specify the root directories where you want to start extracting files
set "root_directories=<windows/folder/path>" REM for example D:\network\Drive

REM Sets the Min file size represents 512MB
REM Minimum file size in bytes (1GB = 1073741824 bytes)
set "min_file_size=536870912"

REM Path to 7-Zip executable
set "seven_zip_path=C:\Program Files\7-Zip\7z.exe"

REM Verify 7-Zip exists
if not exist "!seven_zip_path!" (
    echo Error: 7-Zip not found at !seven_zip_path!
    exit /b 1
)

REM Find all RAR and ZIP files larger than min_file_size in the specified directories
for %%D in (%root_directories%) do (
    echo Looking in directory: "%%D"
    
    REM Process RAR files
    for /r "%%D" %%I in (*.rar) do (
        call :ProcessArchive "%%I" "%%~dpI"
    )
    
    REM Process ZIP files
    for /r "%%D" %%I in (*.zip) do (
        call :ProcessArchive "%%I" "%%~dpI"
    )
)

echo Extraction completed.
pause
exit /b 0

:ProcessArchive
setlocal enabledelayedexpansion
set "archive_file=%~1"
set "extract_path=%~2"

REM Get the actual file size
for %%S in ("!archive_file!") do set "file_size=%%~zS"

echo Found archive: "!archive_file!"
echo Size: !file_size! bytes

REM Check if the file size is greater than or equal to min_file_size
if defined file_size if !file_size! geq %min_file_size% (
    echo Processing "!extract_path!"
    "!seven_zip_path!" x "!archive_file!" -o"!extract_path!"
    set seven_zip_exit_code=!errorlevel!
    if !seven_zip_exit_code! neq 0 (
        echo Error: 7-Zip exited with code !seven_zip_exit_code! while processing "!archive_file!"
    ) else (
        echo Successfully extracted "!archive_file!"
    )
) else (
    echo Skipped "!archive_file!" - file size below threshold
)
endlocal
exit /b 0
