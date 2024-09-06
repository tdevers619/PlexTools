@echo off
setlocal enabledelayedexpansion

REM Specify the root directories where you want to start unraring files
set "root_directories=<windows/folder/path>" # for example D:\network\Drive

REM Sets the Min file size represents 512MB
REM Minimum file size in bytes (1GB = 1073741824 bytes)
set "min_file_size=536870912"

REM Path to 7-Zip executable
set "seven_zip_path=C:\Program Files\7-Zip\7z.exe"

REM Find all RAR files larger than min_file_size in the specified directories and their subdirectories
for %%D in (%root_directories%) do (
    echo Looking in directory: "%%D"
    for /r "%%D" %%I in (*.rar) do (
        echo Found RAR file: "%%I"
        REM Get the size of the file in bytes using 7-Zip
        set "file_size="
        for /f "tokens=3" %%A in ('"!seven_zip_path!" l -slt "%%I" ^| findstr /c:"Size ="') do (
            set "file_size=%%A"
        )

        echo Size of "%%I" is !file_size! bytes

        REM Check if the file size is greater than or equal to min_file_size
        if defined file_size if !file_size! geq %min_file_size% (
            echo Processing "%%~dpI"
            "!seven_zip_path!" x "%%I" -o"%%~dpI"
            set seven_zip_exit_code=!errorlevel!
            if !seven_zip_exit_code! neq 0 (
                echo Error: 7-Zip exited with code !seven_zip_exit_code! While processing "%%I"
            ) else (
                echo Successfully extracted "%%I"
            )
        )
    )
)

echo Unraring completed.
pause
