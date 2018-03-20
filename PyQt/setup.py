from cx_Freeze import setup,Executable

setup(name = 'FTP-Client',
      version = '0.1',
      description = 'FTP client',
      executables = [Executable('main.py')])
