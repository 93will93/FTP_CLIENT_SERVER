from socket import *
import os
import threading


BUFFERSIZE = 8192
codeType = 'UTF-8'

serverPort = 21
serverHost = '127.0.0.1'
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))

serverSocket.listen(5)
print("Server is ready to recieve")


# class FTP_Server(threading.Thred):
#     def __init__(self, clientSocket, clientAdress):
#         threading.Thread.__init__(self)
#         self.PASV = False
#         self.CWD = os.getenv('HOME')
#         self.clientSocket = clientSocket
#         self.clientAdress = clientAdress
#         print('New Connection Added from: ', self.clientAdress)
#
#     def run(self):
#
#
#
#     def welcomeMessage(self):
#
#     def sendFTPCommand(self,command):
#         self.cl
#








connectServerSocket, address = serverSocket.accept()
print(connectServerSocket.recv(BUFFERSIZE).decode(codeType))
connectServerSocket.close()