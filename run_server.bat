@ECHO OFF
setlocal
CALL activate imagine_37
set PYTHONPATH=C:\Users\pinojc\PycharmProjects\PycharmProjects\Magine;%PYTHONPATH%
python manage.py runserver
endlocal


