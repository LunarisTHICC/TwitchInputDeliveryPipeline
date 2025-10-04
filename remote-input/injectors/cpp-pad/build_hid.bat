:: injectors/build_hid.bat
@echo off
setlocal
cl /nologo /O2 /EHsc injector_hid.cpp ws2_32.lib
echo Built injector_hid.exe
