import socket
import os
import threading
import TCP_server
import TCP_client
import random
import sys
import logging

BUFFERSIZE = 8192
codeType = 'UTF-8'
Line_terminator = '\r\n'

serverPort = 12000
serverHost = '127.0.0.1'
commandList = ['USER', 'PASS', 'PWD', 'PASV', 'LIST', 'SYST', 'TYPE',
               'RETR', 'STOR', 'QUIT', 'CWD', 'CDUP', 'MKD', 'RMD', 'DELE'
               , 'NOOP', 'PORT', 'MODE', 'STRU','RNFR', 'RNTO']
# serverSocket = socket(AF_INET, SOCK_STREAM)
# serverSocket.bind(('', serverPort))

ftp_server_connection = TCP_server.TCP(serverHost, serverPort)
ftp_server_connection.bindSocket('', serverPort)

print("Server is ready to recieve")


class FTP_Server(threading.Thread):
    def __init__(self, serverSocket, clientSocket, clientAdress):
        threading.Thread.__init__(self)
        self.loggedIn = False
        self.isPASV = False
        self._CWD = os.getenv('HOME')

        self._PWD = os.getcwd()
        self.incommingCommand = ' '
        # Mode must be ASCII by default
        self.mode = 'A'

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
        self.clientChosenPort = None
        self.isActive = False
        self.activeDataChannel = None
        print('New Connection Added from: ', self.clientAdress)
        self.fileName = str(self.clientAdress) + '.txt'
        print(self.fileName)
        logging.basicConfig(filemode='w', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.DEBUG)
        # logging.info('Testing')
        # self.logger1 = logging.getLogger(self.fileName)
        self.logger = logging.getLogger(self.fileName)
        handler = logging.FileHandler(self._PWD+'/' +self.fileName)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info('12343123')


    def run(self):
        self.welcomeMessage()

        while True:
            try:
                incommingCommand = self.ftp_client_control_connection.receive()


            except socket.error as err:
                print(err)

            try:
                cmd, arg = incommingCommand[:4].strip().upper(), incommingCommand[4:].strip() or None
                if cmd in commandList:
                    commandFunction = getattr(self, cmd)
                    if cmd == 'QUIT':
                        commandFunction()
                        break
                    if arg == None:
                        commandFunction()
                    elif arg != None:
                        commandFunction(arg)
                elif cmd not in commandList:
                    self.clientSocket.send(("502 Command not implemented " + Line_terminator).encode(codeType))
                    self.logger.info(cmd + '502 Command not implemented')
            except AttributeError as err:
                print(err)

    def welcomeMessage(self):
        self.clientSocket.send(("220 Welcome to the Server " + Line_terminator).encode(codeType))
        self.logger.info('220 Welcome to the Server')
        # self.ftp_client_control_connection.transmit("220 Welcome message")

    def USER(self, username):

        if username == "test":
            # self.ftp_client_control_connection.transmitAll("331 User name okay, need password")
            # self.clientSocket.send(("331 User name okay, need password " + Line_terminator).encode(codeType))
            self.transmitControlCommand("331 User name okay, need password ")
            self.logger.info('USER 331 User name okay, need password')
        if username == '':
            # self.ftp_client_control_connection.transmitAll("501 Syntax error in parameters")
            self.clientSocket.send(("501 Syntax error in parameters " + Line_terminator).encode(codeType))
            self.logger.warning('USER 501 Syntax error in parameters ')
    def PASS(self, password):

        if password == "12345":
            # self.ftp_client_control_connection.transmitAll('230 User logged in')
            self.clientSocket.send(("230 User Logged in " + Line_terminator).encode(codeType))
            self.logger.info('PASS 230 User Logged in')
            self.loggedIn = True
        elif password == '':
            # self.ftp_client_control_connection.transmitAll('501 Syntax error in parameters')
            self.clientSocket.send(("501 Syntax error in parameters" + Line_terminator).encode(codeType))
        else:
            # self.ftp_client_control_connection.transmitAll('530 User not logged in')
            self.clientSocket.send(('530 User not logged in' + Line_terminator).encode(codeType))
            self.loggedIn = False

    def PWD(self):
        # self._PWD = os.getcwd()
        self.clientSocket.send(
            ('257' + ' "' + self._PWD + '" ' + 'is the working directory' + Line_terminator).encode(codeType))
        # self.ftp_client_control_connection.transmitAll('257' + ' "' + self._PWD + '" ' + 'is the working directory')
        print(os.getenv('HOME'))
        print(os.getcwd())

    def CWD(self, path):
        newPath = os.path.join(self._PWD, path)
        if not os.path.exists(newPath):
            self.transmitControlCommand('550 Directory does not exist')
            return
        self._CWD = newPath
        self._PWD = newPath
        # os.chdir(self._PWD)
        self.transmitControlCommand('250 Requested file action okay, completed')

    def CDUP(self):
        print(os.getcwd())
        # os.chdir('..')
        self._PWD = os.path.abspath(os.path.join(self._PWD,'..'))

        # self._PWD = os.getcwd()
        self.transmitControlCommand('200 Changed directory to parent directory')
        print(self._PWD)

    def MKD(self, path):
        newPath = os.path.join(self._PWD, path)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
            self.transmitControlCommand('257 ' + path + ' has been created')
        else:
            self.transmitControlCommand('550 file could not be created')

    def RMD(self, folderName):
        folderToBeDeleted = os.path.join(self._PWD, folderName)
        if not os.path.exists(folderToBeDeleted) or folderToBeDeleted == self._PWD:
            self.transmitControlCommand('550 Folder does not exist')
            return
        else:
            os.rmdir(folderToBeDeleted)
            self.transmitControlCommand('257 ' + folderName + ' folder has been deleted')

    def DELE(self, fileName):
        fileToBeDeleted = os.path.join(self._PWD, fileName)
        if not os.path.exists(fileToBeDeleted):
            self.transmitControlCommand('550 ' + fileName + ' does not exist')
            return
        else:
            os.remove(fileToBeDeleted)
            self.transmitControlCommand('250 ' + fileName + ' has been deleted')

    def openPASVDataChannel(self):
        self.serverSock.acceptConnection()
        self.dataSock = self.serverSock.getClientSocket()
        self.address = self.serverSock.getClientAdress()

    def closePASVDataChannel(self):
        self.dataSock.close()
        self.serverSock.close()

    def openActiveDataChannel(self):
        self.activeDataChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.activeDataChannel.connect((serverHost, self.clientChosenPort))

    def closeActiveDataChannel(self):
        self.activeDataChannel.close()

    def LIST(self):

        self.clientSocket.send(("150 List is here" + Line_terminator).encode(codeType))

        if self.isActive == True:
            self.openActiveDataChannel()
            directoryList = os.listdir(self._PWD)
            for i in directoryList:
                self.activeDataChannel.sendall((str(i) + Line_terminator).encode(codeType))
            self.clientSocket.send(('226 List is done transferring through client port' + Line_terminator).encode(codeType))
            self.closeActiveDataChannel()
        else:
            self.openPASVDataChannel()

            directoryList = os.listdir(self._PWD)
            for i in directoryList:
                self.dataSock.sendall((str(i) + Line_terminator).encode(codeType))

            self.clientSocket.send(('226 List is done transferring' + Line_terminator).encode(codeType))
            self.closePASVDataChannel()

    def RETR(self, filename):
        downloadPath = os.path.join(self._PWD, filename)
        if not os.path.exists(downloadPath):
            self.transmitControlCommand('550 file does not exist')
        try:
            if self.mode == 'I':
                file = open(downloadPath, 'rb')
            else:
                file = open(downloadPath, 'r')
        except OSError as error:
            print(error)

        self.transmitControlCommand('150 Opening data channel socket')
        if self.isActive == True:
            self.openActiveDataChannel()
            data = file.readline(BUFFERSIZE)

            while 1:
                if self.mode == 'I':
                    self.activeDataChannel.sendall((data))  # + Line_terminator).encode(codeType))
                else:
                    self.activeDataChannel.sendall((data + Line_terminator).encode(codeType))
                buf = file.readline(8192)
                if not buf:
                    break
                data = buf
            file.close()
            self.closeActiveDataChannel()
            self.transmitControlCommand('226 Transfer successful from client port')
        else:

            self.openPASVDataChannel()
            data = file.readline(BUFFERSIZE)

            while 1:
                if self.mode == 'I':
                    self.dataSock.sendall((data))  # + Line_terminator).encode(codeType))
                else:
                    self.dataSock.sendall((data + Line_terminator).encode(codeType))
                buf = file.readline(8192)
                if not buf:
                    break
                data = buf
            file.close()
            self.closePASVDataChannel()
            self.transmitControlCommand('226 Transfer successful')

    def STOR(self, filename):
        uploadpath = os.path.join(self._PWD, filename)
        try:
            if self.mode == 'I':
                file = open(uploadpath, 'wb')
            else:
                file = open(uploadpath, 'w')
        except OSError as error:
            print(error)

        self.transmitControlCommand('150 Opening data channel socket')

        if self.isActive == True:
            self.openActiveDataChannel()
            data = self.activeDataChannel.recv(BUFFERSIZE)
            while 1:
                temp = self.activeDataChannel.recv(BUFFERSIZE)
                if not temp:
                    break
                data = data + temp
            file.write(data)
            file.close()
            self.closeActiveDataChannel()
            self.transmitControlCommand('226 Transfer complete')

        else:
            self.openPASVDataChannel()
            data = self.dataSock.recv(BUFFERSIZE)
            while 1:
                temp = self.dataSock.recv(BUFFERSIZE)
                if not temp:
                    break
                data = data + temp
            file.write(data)
            file.close()
            self.closePASVDataChannel()
            self.transmitControlCommand('226 Transfer complete')

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
        self.serverSock = TCP_server.TCP(serverHost, self.newPort)
        self.serverSock.bindSocket(serverHost, self.newPort)
        self.serverSock.listen(5)
        tempServerhost = serverHost.replace('.', ',')
        self.transmitControlCommand('227 Entering passive mode' + '(' + tempServerhost + ','
                                    + str(self.newPortNumber1) + ',' + str(self.newPortNumber2) + ')')

    def SYST(self):
        self.transmitControlCommand('215 ' + sys.platform)

    def TYPE(self, type):
        self.mode = type
        if self.mode == 'A':
            self.transmitControlCommand('200 ASCII mode set')
        elif self.mode == 'I':
            self.transmitControlCommand('200 Binary mode set')
        elif self.mode == 'E':
            self.transmitControlCommand('504 Type format not implemented')
        else:
            self.transmitControlCommand('500 Unknown Type')

    def MODE(self, modeCode):
        if modeCode == 'S':
            self.transmitControlCommand('200 Command okay')
        elif modeCode == 'B' or modeCode == 'C':
            self.transmitControlCommand('504 MODE not implemented')
        else:
            self.transmitControlCommand('500 Unknown MODE type')

    def STRU(self, struCode):
        if struCode == 'F':
            self.transmitControlCommand('200 Command okay')
        elif struCode == 'R' or struCode == 'P':
            self.transmitControlCommand('504 MODE not implemented')
        else:
            self.transmitControlCommand('500 Unknown MODE type')
    def RNFR(self, name):
        fileToRename = os.path.join(self._PWD, name)
        if not os.path.exists(fileToRename):
            self.transmitControlCommand('550 File does not exist')
        else:
            self.rnfr = fileToRename
            self.transmitControlCommand('350 Action Pending further information')

    def RNTO(self, name):
        newName = os.path.join(self._PWD, name)
        if os.path.exists(newName):
            self.transmitControlCommand('553 File name not allowed')
        else:
            os.rename(self.rnfr, newName)
            self.transmitControlCommand('250 File renamed')



    def NOOP(self):
        self.transmitControlCommand('200 OK')

    def PORT(self, portCommand):
        self.isActive = True
        client_chosen_port  = portCommand.split(',')
        temp = ''
        for i in range(0, 4):
            temp = temp + (client_chosen_port[i]) + '.'
        server_ip = temp + client_chosen_port[3]
        print(server_ip)
        server_resp_port = client_chosen_port[-2:]
        newport = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))

        print('Client ', self.clientAdress, ' will now pass data over port ' + str(newport))
        self.clientChosenPort = int(newport)
        self.transmitControlCommand('200 Port ' + str(self.clientChosenPort) + ' will now be used')

    def transmitControlCommand(self, message):
        self.clientSocket.sendall((message + Line_terminator).encode(codeType))

    def QUIT(self):
        self.transmitControlCommand('221 User logged out')

        print(self.clientAdress, 'has been disconnected')
        self.ftp_client_control_connection.close()


while 1:
    ftp_server_connection.listen(1)
    ftp_server_connection.acceptConnection()
    newThread = FTP_Server(ftp_server_connection.getServerSocket(), ftp_server_connection.getClientSocket(),
                           ftp_server_connection.getClientAdress())
    newThread.start()


