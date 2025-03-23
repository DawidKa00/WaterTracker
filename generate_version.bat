@echo off
set VENV_DIR=%~dp0.venv1

:: Sprawdzenie, czy już jesteśmy w virtualenv
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
)

:: Uruchomienie Pythona w virtualenv
python -c "import setuptools_scm; print(setuptools_scm.get_version())" > version.txt
set /p VERSION=<version.txt
echo Project version: %VERSION%

exit
