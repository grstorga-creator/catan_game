@echo off
REM BUILD_DEMO.bat - Automated build script for Catan demo distribution
REM Run this from C:\catan_game\catan_game\

echo.
echo ========================================
echo Building Catan Demo Package
echo ========================================
echo.

REM Step 1: Rebuild the executable with PyInstaller
echo [1/5] Building executable with PyInstaller...
pyinstaller --onedir --windowed nodknaKra_renderer_oop.py
if errorlevel 1 (
    echo ERROR: PyInstaller failed. Make sure it's installed: pip install pyinstaller
    pause
    exit /b 1
)
echo [1/5] Complete!
echo.

REM Step 2: Copy Python modules
echo [2/5] Copying Python modules...
copy nodknaKra_game.py dist\nodknaKra_renderer_oop\ >nul
if errorlevel 1 goto CopyError
copy nodknaKra_maps_oop.py dist\nodknaKra_renderer_oop\ >nul
if errorlevel 1 goto CopyError
copy nodknaKra_vertices_edges.py dist\nodknaKra_renderer_oop\ >nul
if errorlevel 1 goto CopyError
echo [2/5] Complete!
echo.

REM Step 3: Create launcher script
echo [3/5] Creating launcher script (RUN_GAME.bat)...
(
    echo @echo off
    echo nodknaKra_renderer_oop.exe standard 42
    echo pause
) > dist\nodknaKra_renderer_oop\RUN_GAME.bat
echo [3/5] Complete!
echo.

REM Step 4: Remove old zip if it exists
echo [4/5] Cleaning up old package...
if exist catan_demo.zip del catan_demo.zip
echo [4/5] Complete!
echo.

REM Step 5: Create new zip
echo [5/5] Creating distribution package (catan_demo.zip)...
powershell Compress-Archive -Path dist\nodknaKra_renderer_oop -DestinationPath catan_demo.zip
if errorlevel 1 (
    echo ERROR: Failed to create zip file
    pause
    exit /b 1
)
echo [5/5] Complete!
echo.

echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Package ready: catan_demo.zip
echo.
echo To distribute:
echo   1. Send catan_demo.zip to your friend
echo   2. They extract the zip
echo   3. They double-click RUN_GAME.bat
echo.
pause
