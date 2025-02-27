@echo off
echo Yandex Images Downloader
echo ----------------------
echo.

set /p search="Enter search term or URL: "
set /p count="Enter number of images to download (default: 10): "
set /p size="Enter minimum image size (format: WxH, default: 0x0): "
set /p dir="Enter output directory (default: downloaded_images): "

if "%count%"=="" set count=10
if "%size%"=="" set size=0x0
if "%dir%"=="" set dir=downloaded_images

echo.
echo Starting download...
echo.

python example_usage.py --search "%search%" --count %count% --size "%size%" --dir "%dir%"

echo.
echo Press any key to exit...
pause > nul
