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
commandList = ['USER', 'PASS', 'PWD', 'PASV', 'LIST', 'TYPE',
               'RETR', 'STOR', 'QUIT', 'CWD', 'CDUP', 'MKD', 'RMD', 'DELE'
               , 'NOOP', 'PORT', 'MODE', 'STRU','RNFR', 'RNTO', 'SYST', 'HELP']

ftp_server_connection = TCP_server.TCP(serverHost, serverPort)
ftp_server_connection.bindSocket('', serverPort)

credentails = open('credentials.txt','r')
usernameList=[]
passwordList = []


for line in credentails:
    x = line.split()
    usernameList.append(x[0])
    passwordList.append(x[1])


print("Server is ready to recieve")


class FTP_Server(threading.Thread):
    def __init__(self, serverSocket, clientSocket, clientAdress):
        threading.Thread.__init__(self)
        self.loggedIn = False
        self.isPASV = False
        self._CWD = os.getenv('HOME')
        print(self._CWD)
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
        self.userCount = 0

    def run(self):
        self.welcomeMessage()

        while True:
            try:
                incommingCommand = self.ftp_client_control_connection.receive()
            except socket.error as error:
                print(error)
            try:
                ftpcommand = incommingCommand[:4].strip().upper()
                functionArguments = incommingCommand[4:].strip() or None
                if ftpcommand in commandList:
                    commandFunction = getattr(self, ftpcommand)
                    if ftpcommand == 'QUIT':
                        commandFunction()
                        break
                    if functionArguments == None:
                        commandFunction()
                    elif functionArguments != None:
                        commandFunction(functionArguments)
                elif ftpcommand not in commandList:
                    self.clientSocket.send(("502 Command not implemented " + Line_terminator).encode(codeType))

            except AttributeError as error:
                print(error)

    def welcomeMessage(self):
        self.transmitControlCommand('220 Welcome to FTP Global by CAIO')

    def initiliizeLogger(self, username):
        fileName = username + '.txt'
        print(fileName)
        logging.basicConfig(filemode='a')
        self.logger = logging.getLogger(fileName)
        folderPath = self._PWD + '/Logs'
        pathname = folderPath + '/' + fileName
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        handler = logging.FileHandler(pathname)
        formatter = logging.Formatter('%(asctime)s %(levelname)s' + ' ' + username + ' %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)

    def USER(self, username):

        self.initiliizeLogger(username)

        self.logger.info('Command USER ' + username)
        for z in usernameList:
            if z == username:
                break
            self.userCount +=1

        if username == usernameList[self.userCount]:
            self.transmitControlCommand("331 User name okay, need password ")
            self.logger.info('Response USER 331 User name okay, need password')
        if username == '':
            self.transmitControlCommand('501 Syntax error in paramaters')
            self.logger.warning('Response USER 501 Syntax error in parameters ')

    def PASS(self, password):
        self.logger.info('Command PASS *****')

        if password == passwordList[self.userCount]:
            self.transmitControlCommand('230 User Logged In')
            self.logger.info('Response PASS 230 User Logged in')
            self.loggedIn = True
        elif password == '':
            self.transmitControlCommand('501 Syntax error in parameters')
            self.logger.error('Response PASS 501 Syntax error in parameters')
        else:
            self.transmitControlCommand('530 User not logged in')
            self.loggedIn = False
            self.logger.warning('Response PASS 530 User not logged in')

    def PWD(self):
        self.logger.info('Command PWD')
        self.transmitControlCommand('257' + ' "' + self._PWD + '" ' + 'is the working directory')
        self.logger.info('Response PWD 257 ' + self._PWD)

    def CWD(self, path):
        self.logger.info('Command CWD ' + path)
        newPath = os.path.join(self._PWD, path)
        if not os.path.exists(newPath):
            self.transmitControlCommand('550 Directory does not exist')
            self.logger.error('Response CWD 550 Directory does not exist')
            return
        self._CWD = newPath
        self._PWD = newPath
        self.transmitControlCommand('250 Requested file action okay, completed')
        self.logger.info('Response CWD 250 File action okay')

    def CDUP(self):
        self.logger.info('Command CDUP')
        self._PWD = os.path.abspath(os.path.join(self._PWD,'..'))
        self.transmitControlCommand('200 Changed directory to parent directory')
        self.logger.info('Response CDUP 200 Changed to parent directory ' +self._PWD )

    def MKD(self, path):
        self.logger.info('Command MKD ' + path)
        newPath = os.path.join(self._PWD, path)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
            self.transmitControlCommand('257 ' + path + ' has been created')
            self.logger.info('Response MKD 257 ' +path + ' created')
        else:
            self.transmitControlCommand('550 file could not be created')
            self.logger.warning('Response MKD 550 file could not be created')

    def RMD(self, folderName):
        self.logger.info('Command RMD ' + folderName)
        folderToBeDeleted = os.path.join(self._PWD, folderName)
        if not os.path.exists(folderToBeDeleted) or folderToBeDeleted == self._PWD:
            self.transmitControlCommand('550 Folder does not exist')
            self.logger.warning('Response RMD 550 folder does not exist')
            return
        else:
            os.rmdir(folderToBeDeleted)
            self.transmitControlCommand('257 ' + folderName + ' folder has been deleted')
            self.logger.info('Response RMD 257 '+ folderName +' created')

    def DELE(self, fileName):
        self.logger.info('Command DELE ' + fileName)
        if self.loggedIn == False:
            self.transmitControlCommand('530 User not logged in')
            self.logger.warning('Response DELE 530 Not logged in')
            return
        fileToBeDeleted = os.path.join(self._PWD, fileName)
        if not os.path.exists(fileToBeDeleted):
            self.transmitControlCommand('550 ' + fileName + ' does not exist')
            self.logger.warning('Response DELE 550 ' +fileName + ' does not exist' )
            return
        else:
            os.remove(fileToBeDeleted)
            self.transmitControlCommand('250 ' + fileName + ' has been deleted')
            self.logger.info('Response DELE 250 '+ fileName + 'Deleted')

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
        self.logger.info('Command LIST')
        if self.loggedIn == False:
            self.transmitControlCommand('530 User not logged in')
            self.logger.warning('Response LIST 530 Not logged in')
            return
        self.transmitControlCommand('150 list is here')
        self.logger.info('Response LIST 150 list is here')
        if self.isActive == True:
            self.openActiveDataChannel()
            directoryList = os.listdir(self._PWD)
            for i in directoryList:
                self.activeDataChannel.sendall((str(i) + Line_terminator).encode(codeType))
            self.transmitControlCommand('226 List is done transferring through client port')
            self.logger.info('Response LIST 226 List is done transferring')
            self.closeActiveDataChannel()
        else:
            self.openPASVDataChannel()
            directoryList = os.listdir(self._PWD)
            for i in directoryList:
                self.dataSock.sendall((str(i) + Line_terminator).encode(codeType))
            self.transmitControlCommand('226 List is done transferring')
            self.logger.info('Response LIST 226 List is done transferring')
            self.closePASVDataChannel()

    def RETR(self, filename):
        self.logger.info('Command RETR ' + filename)
        if self.loggedIn == False:
            self.transmitControlCommand('530 User not logged in')
            self.logger.warning('Response RETR 530 Not logged in')
            return
        downloadPath = os.path.join(self._PWD, filename)
        if not os.path.exists(downloadPath):
            self.transmitControlCommand('550 file does not exist')
            self.logger.error('Response RETR 550 file does not exist')
        try:
            if self.mode == 'I':
                file = open(downloadPath, 'rb')
            else:
                file = open(downloadPath, 'r')
        except OSError as error:
            print(error)

        self.transmitControlCommand('150 Opening data channel socket')
        self.logger.info('Response RETR 150 Opening data channel')
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
            self.logger.info('Response RETR 226 Transfer of ' + filename+' successful')
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
            self.logger.info('Response RETR 226 Transfer of ' + filename + ' successful')

    def STOR(self, filename):
        self.logger.info('Command STOR ' + filename)
        if self.loggedIn == False:
            self.transmitControlCommand('530 User not logged in')
            self.logger.warning('Response STOR 530 Not logged in')
            return
        uploadpath = os.path.join(self._PWD, filename)
        try:
            if self.mode == 'I':
                file = open(uploadpath, 'wb')
            else:
                file = open(uploadpath, 'w')
        except OSError as error:
            print(error)

        self.transmitControlCommand('150 Opening data channel socket')
        self.logger.info('Response STOR 150 Opening data channel')
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
            self.logger.info('Response STOR 226 Transfer of ' + filename + ' successful')

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
            self.logger.info('Response STOR 226 Transfer of ' + filename + ' successful')

    def PASV(self):
        self.logger.info('Command PASV')
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
        self.logger.info('Response PASV 227 Entering passive mode' + '(' + tempServerhost + ','
                                    + str(self.newPortNumber1) + ',' + str(self.newPortNumber2) + ')')
    def SYST(self):
        self.logger.info('Command SYST')
        self.transmitControlCommand('215 ' + sys.platform)
        self.logger.info('Response SYST 215')

    def TYPE(self, type):
        self.mode = type
        self.logger.info('Command TYPE ' + type)
        if self.mode == 'A':
            self.transmitControlCommand('200 ASCII mode set')
            self.logger.info('Response TYPE 200 ASCII mode set')
        elif self.mode == 'I':
            self.transmitControlCommand('200 Binary mode set')
            self.logger.info('Response TYPE 200 Binary mode set')
        elif self.mode == 'E':
            self.transmitControlCommand('504 Type format not implemented')
            self.logger.info('Response TYPE 504 Type format not implemented')
        else:
            self.transmitControlCommand('500 Unknown Type')
            self.logger.warning('Response TYPE 500 Unknown Type')

    def MODE(self, modeCode):
        self.logger.info('Command MODE '+ modeCode)
        if modeCode == 'S':
            self.transmitControlCommand('200 Command okay')
            self.logger.info('Response MODE 200 command okay')
        elif modeCode == 'B' or modeCode == 'C':
            self.transmitControlCommand('504 MODE not implemented')
            self.logger.info('Response MODE 504 Mode not implemented')
        else:
            self.transmitControlCommand('500 Unknown MODE type')
            self.logger.info('Response MODE 504 Unknown Mode type')

    def STRU(self, struCode):
        self.logger.info('Command STRU ' + struCode)
        if struCode == 'F':
            self.transmitControlCommand('200 Command okay')
            self.logger.info('Response STRU 200 command okay')
        elif struCode == 'R' or struCode == 'P':
            self.transmitControlCommand('504 MODE not implemented')
            self.logger.info('Response STRU 504 MODE not implemented')
        else:
            self.transmitControlCommand('500 Unknown MODE type')
            self.logger.info('Response STRU 500 Unknown MODE type')

    def RNFR(self, name):
        fileToRename = os.path.join(self._PWD, name)
        self.logger.info('Command RNFR ' + fileToRename)
        if not os.path.exists(fileToRename):
            self.transmitControlCommand('550 File does not exist')
            self.logger.warning('Response RNFR 550 file does not exist')
        else:
            self.rnfr = fileToRename
            self.transmitControlCommand('350 Action Pending further information')
            self.logger.warning('Response RNFR 350 awaiting further action ')

    def RNTO(self, name):
        newName = os.path.join(self._PWD, name)
        self.logger.info('Command RNTO ' + newName)
        if os.path.exists(newName):
            self.transmitControlCommand('553 File name not allowed')
            self.logger.warning('Response RNTO 553 file name not allowed')
        else:
            os.rename(self.rnfr, newName)
            self.transmitControlCommand('250 File renamed')
            self.logger.warning('Response RNTO 250 file renamed')

    def NOOP(self):
        self.logger.info('Command NOOP')
        self.transmitControlCommand('200 OK')
        self.logger.info('Response NOOP 200 OK')

    def PORT(self, portCommand):
        self.logger.info('Command PORT ' + portCommand)
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
        self.logger.info('Response PORT 200 Port ' + str(self.clientChosenPort) + ' will now be used')

    def HELP(self):
        self.logger.info('Command HELP')
        self.transmitControlCommand('214 Help is comming' + str(commandList) + '214 enjoy FTP Global')
        self.logger.info('Response HELP 214')

    def transmitControlCommand(self, message):
        self.clientSocket.sendall((message + Line_terminator).encode(codeType))

    def QUIT(self):
        self.logger.info('Command QUIT')
        self.transmitControlCommand('221 User logged out')
        self.logger.info('Response QUIT 221 User logged out')
        print(self.clientAdress, 'has been disconnected')
        self.ftp_client_control_connection.close()


while 1:
    ftp_server_connection.listen(1)
    ftp_server_connection.acceptConnection()
    newThread = FTP_Server(ftp_server_connection.getServerSocket(), ftp_server_connection.getClientSocket(),
                           ftp_server_connection.getClientAdress())
    newThread.start()


