from socket import *
import os
import threading
import TCP_server
import TCP_client


BUFFERSIZE = 8192
codeType = 'UTF-8'

serverPort = 12000
serverHost = '127.0.0.1'
# serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.bind(('', serverPort))

ftp_server_connection = TCP_server.TCP(serverHost,serverPort)


print("Server is ready to recieve")


class FTP_Server(threading.Thread):
    def __init__(self, clientSocket, clientAdress):
        threading.Thread.__init__(self)
        self.PASV = False
        self.CWD = os.getenv('HOME')
        self.clientSocket = clientSocket
        self.clientAdress = clientAdress
        print('New Connection Added from: ', self.clientAdress)

    def run(self):
        self.welcomeMessage()




    def welcomeMessage(self):
        ftp_client_connection.transmitAll("Welcome message")
    #
    # def sendFTPCommand(self,command):
    #     self.cl


while 1:
    ftp_server_connection.listen(1)

    ftp_client_connection = TCP_client.TCP(ftp_server_connection.getServerSocket())

    ftp_client_connection.acceptConnection()

    print(ftp_client_connection.receive())

    newThread = FTP_Server(ftp_client_connection.getSocket(),ftp_client_connection.getAdress())
    newThread.start()
    # ftp_client_connection.transmitAll("Welcome")

# ftp_client_connection.close()
# ftp_server_connection.close()



