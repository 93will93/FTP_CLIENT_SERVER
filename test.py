import FTPclient

FTP_SERVER_ADDRESS = "ftp.mirror.ac.za"
FTP_PORT = 21
client = FTPclient.FTPclient(FTP_SERVER_ADDRESS)
client.pasv()
client.list()
client.quit()
