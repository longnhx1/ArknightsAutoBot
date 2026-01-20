@echo off
echo ==========================================
echo      DANG BUILD LOCAL (KHONG CAN GITHUB)
echo ==========================================

:: 1. Build Python Logic
echo.
echo [1/4] Dang build Python Logic...
cd ArknightsBot.Logic
pyinstaller --onefile --name ArknightsBot.Logic ArknightsBot.Logic.py
if %errorlevel% neq 0 goto :error
cd ..

:: 2. Build C# UI
echo.
echo [2/4] Dang build C# UI...
cd ArknightsBot.UI
dotnet publish -c Release -r win-x64 --self-contained false -o ./publish
if %errorlevel% neq 0 goto :error
cd ..

:: 3. Gom file vao thu muc Release_Local
echo.
echo [3/4] Dang gom file...
if exist Release_Local rmdir /s /q Release_Local
mkdir Release_Local
mkdir Release_Local\bin
mkdir Release_Local\adb
mkdir Release_Local\templates

copy ArknightsBot.Logic\dist\ArknightsBot.Logic.exe Release_Local\
copy ArknightsBot.UI\publish\ArknightsBot.UI.exe Release_Local\
copy ArknightsBot.UI\publish\HandyControl.dll Release_Local\
copy ArknightsBot.UI\publish\ArknightsBot.UI.deps.json Release_Local\
copy ArknightsBot.UI\publish\ArknightsBot.UI.runtimeconfig.json Release_Local\
copy ArknightsBot.UI\publish\ArknightsBot.UI.dll Release_Local\

copy bin\* Release_Local\bin\
copy templates\* Release_Local\templates\
xcopy /E /I /Y adb Release_Local\adb
copy settings.json Release_Local\

:: 4. Xong
echo.
echo ==========================================
echo      BUILD THANH CONG!
echo      File nam trong thu muc: Release_Local
echo ==========================================
pause
exit

:error
echo.
echo !!! CO LOI XAY RA !!!
pause