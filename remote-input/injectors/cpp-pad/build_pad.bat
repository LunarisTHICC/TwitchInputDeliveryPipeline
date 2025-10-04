:: injectors/build_pad.bat
@echo off
setlocal
:: Update path to ViGEm headers and lib if not in default include/lib paths
cl /nologo /O2 /EHsc injector_pad.cpp ws2_32.lib ViGEmClient.lib
echo Built injector_pad.exe
