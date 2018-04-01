'''
FTP Server
Authors: Sailen Nair (1078491) William Becerra (789146)
'''
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

serverPort = 21
serverHost = socket.gethostbyname(socket.gethostname())

# List of commands that the server can handle
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

'''
This is the main class. This class contains all the functions that execute the commands that are received.
'''
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

    '''
    This is the function that will run when a new thread is created. The function will listen for a 
    command from the client, then it will execute the function which is related to the command or will send 
    an appropriate response back to the server
    '''
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
                    # the getattr() function takes two arguments and combines them to make a single function
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
    # A standard welcome message
    def welcomeMessage(self):
        self.transmitControlCommand('220 Welcome to FTP Global by CAIO')

    # This function intilises the logger, it will create/ open the a textfile to log all the commands/ responses.
    # each client will have their own log file.
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

    # This function recieves the username and checks if it is in the username list, it will then ask for the password
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
            self._PWD = os.path.join(self._PWD, username)
            if not os.path.exists(self._PWD):
                os.makedirs(self._PWD)

        elif username not in usernameList:
            self.transmitControlCommand('501 Syntax error in paramaters')
            self.logger.warning('Response USER 501 Syntax error in parameters ')

    # This function will check if the password sent is correct, if it is then it will log the user in, else the user will
    # not be logged in.
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

    # This function will print the working directory. The working directory is kept as a class variable, thus each thread
    # will have their own working directory.
    def PWD(self):
        self.logger.info('Command PWD')
        self.transmitControlCommand('257' + ' "' + self._PWD + '" ' + 'is the working directory')
        self.logger.info('Response PWD 257 ' + self._PWD)

    # This function makes use of the 'os' library to change the current directory to the required one.
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

    # This function changes the current working directory to the parent directory.
    def CDUP(self):
        self.logger.info('Command CDUP')
        self._PWD = os.path.abspath(os.path.join(self._PWD,'..'))
        self.transmitControlCommand('200 Changed directory to parent directory')
        self.logger.info('Response CDUP 200 Changed to parent directory ' +self._PWD )

    # This function makes a new directory using the 'os' library. It will check if the folder already exists first.
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

    # This function will delete an entire folder
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

    # This function will delete teh file which is specified
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

    # This function will accept a data connection from a client (passive mode).
    def openPASVDataChannel(self):
        try:
            self.serverSock.acceptConnection()
            self.dataSock = self.serverSock.getClientSocket()
            self.address = self.serverSock.getClientAdress()
        except socket.error as error:
            self.transmitControlCommand('425 Cant open data connection')
            print(error)

    # This function will close the passive data connection.
    def closePASVDataChannel(self):
        self.dataSock.close()
        self.serverSock.close()

    # This function will create a new socket for clients to connect to (active mode)
    def openActiveDataChannel(self):
        self.activeDataChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.activeDataChannel.connect((self.clientAdress[0], self.clientChosenPort))

    # This funciton will close the socket made for active mode.
    def closeActiveDataChannel(self):
        self.activeDataChannel.close()

    # This function will send the list of all the files and folders of the users working directories. It can do so in
    # both passive and active
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

    # This function will send a file to the client, it can do so in both passive and active.
    # It first checks if the user is logged on, and then proceeds to check if the file that wants to be downloaded
    # exists. It will use either binery mode or ascii mode
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

    # This function will receive a file from the client, it can do so in both passive and active.
    # It first checks if the user is logged on. It will use either binery mode or ascii mode
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

    # This function will create a new socket for the client to connect to, which will act as the data connection socket.
    def PASV(self):
        self.logger.info('Command PASV')
        self.isPASV = True
        self.isActive = False
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
    # This function will return the system platform that the server is running.
    def SYST(self):
        self.logger.info('Command SYST')
        self.transmitControlCommand('215 ' + sys.platform)
        self.logger.info('Response SYST 215')

    # This function will set the mode of download/ upload to be either binery or ASCII, if the mode is not supported
    # it will return an appropriate response.
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

    # This function will change the mode to the clients choice, it will send an appropritate response if the mode
    # is not supported
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
            self.logger.info('Response MODE 500 Unknown Mode type')

    # This function will change the file structure to the clients choice, it will send an appropritate response
    # if the mode is not supported
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

    # This function will take in a file that is to be renamed. It needs to be followed up directly with
    # the RNTO command
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

    # This function will change the name of the file to the name wanted by the client.
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

    # This function does not do anything apart from sending an appropriate response
    def NOOP(self):
        self.logger.info('Command NOOP')
        self.transmitControlCommand('200 OK')
        self.logger.info('Response NOOP 200 OK')

    # This function puts the server into active mode and tries to connect to the client to a specific port
    def PORT(self, portCommand):
        self.logger.info('Command PORT ' + portCommand)
        self.isActive = True
        self.isPASV = False
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

    # This function will send back the list of commands that the server can handle.
    def HELP(self):
        self.logger.info('Command HELP')
        self.transmitControlCommand('214 Help is comming' + str(commandList) + '214 enjoy FTP Global')
        self.logger.info('Response HELP 214')

    # This function will send the responses over the control command
    def transmitControlCommand(self, message):
        self.clientSocket.sendall((message + Line_terminator).encode(codeType))

    # This function will log the client out of the server.
    def QUIT(self):
        self.logger.info('Command QUIT')
        self.transmitControlCommand('221 User logged out')
        self.logger.info('Response QUIT 221 User logged out')
        print(self.clientAdress, 'has been disconnected')
        self.ftp_client_control_connection.close()

# This will keep the server on at all times, it will listen for new connections and create a new thread everytime
# a new connection is made.
while 1:
    ftp_server_connection.listen(1)
    ftp_server_connection.acceptConnection()
    newThread = FTP_Server(ftp_server_connection.getServerSocket(), ftp_server_connection.getClientSocket(),
                           ftp_server_connection.getClientAdress())
    newThread.start()


