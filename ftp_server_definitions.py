import socket
import os
import threading
import TCP_server
import TCP_client
import random


BUFFERSIZE = 8192
codeType = 'UTF-8'
Line_terminator = '\r\n'

serverPort = 12000
serverHost = '127.0.0.1'
commandList = ['USER', 'PASS', 'PWD', 'PASV', 'LIST','SYST']
# serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.bind(('', serverPort))

ftp_server_connection = TCP_server.TCP(serverHost, serverPort)
ftp_server_connection.bindSocket('',serverPort)

print("Server is ready to recieve")


class FTP_Server(threading.Thread):
    def __init__(self, serverSocket, clientSocket, clientAdress):
        threading.Thread.__init__(self)
        self.loggedIn = False
        self.isPASV = False
        self.CWD = os.getenv('HOME')
        self._PWD = os.getcwd()
        self.incommingCommand = ' '

        self.ftp_client_control_connection = TCP_client.TCP(serverSocket, clientSocket, clientAdress)
        # self.ftp_client_control_connection.acceptConnection()

        self.clientSocket = self.ftp_client_control_connection.getSocket()
        self.clientAdress = self.ftp_client_control_connection.getAdress()

        self.server_Passive_Data_Socket = None
        self.newPortNumber1 = 0
        self.newPortNumber2 = 0
        self._pasvServerAdress = None
        self._pasvServerSocket = None
        self.newPort = 0
        print('New Connection Added from: ', self.clientAdress)
        # self.welcomeMessage()

    def run(self):
        self.welcomeMessage()
        # print("Testing")
        # print("Testing2")
        while True:
            try:
                # print("trying")
                incommingCommand = self.ftp_client_control_connection.receive()


            except socket.error as err:
                print(err)

            try:
                cmd, arg = incommingCommand[:4].strip().upper(), incommingCommand[4:].strip() or None
                if cmd in commandList:
                    commandFunction = getattr(self, cmd)
                    if arg == None:
                        commandFunction()
                    elif arg != None:
                        commandFunction(arg)
                elif cmd not in commandList:
                    self.clientSocket.send(("502 Command not implemented " + Line_terminator).encode(codeType))
            except AttributeError as err:
                print(err)

    def welcomeMessage(self):
        self.clientSocket.send(("220 Welcome to the Server "+Line_terminator).encode(codeType))
        # self.ftp_client_control_connection.transmit("220 Welcome message")


    def USER(self, username):
        if username == "test":
            # self.ftp_client_control_connection.transmitAll("331 User name okay, need password")
            self.clientSocket.send(("331 User name okay, need password " + Line_terminator).encode(codeType))
        if username == '':
            # self.ftp_client_control_connection.transmitAll("501 Syntax error in parameters")
            self.clientSocket.send(("501 Syntax error in parameters " + Line_terminator).encode(codeType))

    def PASS(self, password):
        if password == "12345":
            # self.ftp_client_control_connection.transmitAll('230 User logged in')
            self.clientSocket.send(("230 User Logged in " + Line_terminator).encode(codeType))
            self.loggedIn = True
        elif password == '':
            # self.ftp_client_control_connection.transmitAll('501 Syntax error in parameters')
            self.clientSocket.send(("501 Syntax error in parameters" + Line_terminator).encode(codeType))
        else:
            # self.ftp_client_control_connection.transmitAll('530 User not logged in')
            self.clientSocket.send(('530 User not logged in' + Line_terminator).encode(codeType))
            self.loggedIn = False

    def PWD(self):
        self._PWD = os.getcwd()
        self.clientSocket.send(('257' + ' "' + self._PWD + '" ' + 'is the working directory' + Line_terminator).encode(codeType))
        # self.ftp_client_control_connection.transmitAll('257' + ' "' + self._PWD + '" ' + 'is the working directory')

    def LIST(self):

        self.clientSocket.send(("150 List is here" + Line_terminator).encode(codeType))
        # self.ftp_client_control_connection.transmitAll("150 List is here")
        # self.dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.dataSock, self.address = self.serverSock.accept()
        self.serverSock.acceptConnection()
        self.dataSock = self.serverSock.getClientSocket()
        self.address = self.serverSock.getClientAdress()
        directoryList = os.listdir(self._PWD)
        print(directoryList)

        for i in directoryList:
            self.dataSock.sendall((str(i) + Line_terminator).encode(codeType))

        # self.dataSock.sendall(("Hello"+Line_terminator).encode(codeType))
        # self.ftp_client_control_connection.transmitAll('226 List is done transferring')
        self.clientSocket.send(('226 List is done transferring' + Line_terminator).encode(codeType))
        self.dataSock.close()

    def PASV(self):
        self.isPASV = True
        tempPortNum1 = random.randint(8, 256)
        tempPortNum2 = random.randint(1, 256)
        if tempPortNum1 == self.newPortNumber1 and tempPortNum2 == self.newPortNumber2:
            tempPortNum1 = random.randint(8, 255)
            tempPortNum2 = random.randint(1, 256)
        self.newPortNumber1 = tempPortNum1
        self.newPortNumber2 = tempPortNum2
        self.newPort = self.newPortNumber1 * 256 + self.newPortNumber2
        print('new port', self.newPort)

        self.serverSock = TCP_server.TCP(serverHost,self.newPort)
        self.serverSock.bindSocket(serverHost, self.newPort)
        self.serverSock.listen(5)

        # self.serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.serverSock.bind((serverHost, self.newPort))
        # self.serverSock.listen(5)

        tempServerhost = serverHost.replace('.', ',')
        self.ftp_client_control_connection.transmitAll('227 Entering passive mode' + '(' + tempServerhost + ','
                                                       + str(self.newPortNumber1) + ',' + str(self.newPortNumber2) + ')')

    def SYST(self):
        self.clientSocket.send(("215 Windows " + Line_terminator).encode(codeType))

while 1:
    ftp_server_connection.listen(1)
    ftp_server_connection.acceptConnection()
    newThread = FTP_Server(ftp_server_connection.getServerSocket(),ftp_server_connection.getClientSocket(), ftp_server_connection.getClientAdress())
    newThread.start()


    # ftp_client_control_connection = TCP_client.TCP(ftp_server_connection.getServerSocket())
    #
    # ftp_client_control_connection.acceptConnection()

    # print(ftp_client_control_connection.receive())

    # newThread = FTP_Server(ftp_client_control_connection.getSocket(), ftp_client_control_connection.getAdress())

    # ftp_client_connection.transmitAll("Welcome")

# ftp_client_connection.close()
# ftp_server_connection.close()
