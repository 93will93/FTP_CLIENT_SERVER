PyQt Application


*******************************************************************
Steps to create an excecutable.
1. Download cx_Freeze >>> python -m pip install cx_Freese -- upgrade

2. Make sure to work in the same folder as the python application

3. Create a setup.py file with the following script in it:
	from cx_Freeze import setup,Executable
	setup(name = 'FTP-Client',
      		version = '0.1',
      		description = 'FTP client',
      		executables = [Executable('main.py')])
4. Save setup.py

5. Finally run >> python setup.py build

6. Look for executable in the build folder
******************************************************************