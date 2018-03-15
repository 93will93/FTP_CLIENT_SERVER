import ftplib as ftp
serverName = 'localhost'
f = ftp.FTP(serverName)

print(f.connect(serverName,21,10,None))

print( f.login())
print(f.dir())
print(f.acct("anonymous@"))
# print(f.getwelcome())
# print(f.pwd())
# f.sendcmd("CWD")
# print(f.pwd())
f.close()
# ftp.FTP.close()