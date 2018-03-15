from socket import *
import time

serverName = 'localhost'
# serverName = 'ftp.uconn.edu'

serverPort = 21
clientSocket = socket(AF_INET, SOCK_STREAM)
codeType = "UTF-8"
Line_terminator = '\r\n'
ENTERING_PASV_MODE_CODE = 227


class FTP_Client:
    def __init__(self, servername, serverPort, clientSocket = None):
        self.serverName = servername
        self.serverPort = serverPort
        self.clientSocket = clientSocket
        # self.username = "anonymous"
        # self.password = "anonymous@"
        # self.username = "group14"
        # self.password = "engaqu4a"
        self.username = "test"
        self.password = "12345"


        self.account = ""
        self._data_port = None
        self._tcp_data = None
        self.Connect_Control_Socket(self.clientSocket)
        self._tcp_IP = None

    def Connect_Control_Socket(self,clientSocket):
        clientSocket.connect((self.serverName, self.serverPort))
        responseMessage = self.clientSocket.recv(8192).decode(codeType)
        print(responseMessage)
        print("##############")

    def getCredentials(self):
        self.username = input("Please enter your username")
        self.password = input("Please enter your password")

    def login(self):
        self.clientSocket.sendall(('USER ' + self.username + Line_terminator).encode(codeType))
        serverResponse = self.clientSocket.recv(2048).decode(codeType)
        print(serverResponse)
        self.clientSocket.sendall(('PASS ' + self.password + Line_terminator).encode(codeType))
        serverResponse = self.clientSocket.recv(2048).decode(codeType)
        print(serverResponse)
        # self.clientSocket.sendall(('ACCT '+self.account + Line_terminator).encode(codeType))
        # serverResponse = self.clientSocket.recv(2048).decode(codeType)
        # print(serverResponse)

    def closeConnectcion(self):
        self.clientSocket.close()

    def cmdCWD(self,path):
        self.clientSocket.sendall(('CWD'+' '+path+ Line_terminator).encode(codeType))
        cwd = self.clientSocket.recv(2048).decode(codeType)
        print(cwd)

    def cmdPWD(self):
        self.clientSocket.sendall(('PWD'+Line_terminator).encode(codeType))
        workingDirctory = self.clientSocket.recv(8192).decode(codeType)
        print(workingDirctory)


    def cmdLIST(self):
        self.createNewTCPConnection(self._data_port)
        self.clientSocket.sendall(('List '+Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        secondResponse = self.clientSocket.recv(8192).decode(codeType)
        list = self._tcp_data.recv(8192).decode(codeType)
        print(response,'@@@')
        print(secondResponse,'###')
        print(list)
        self._tcp_data.close()
        print("Data Socket closed")

        # self._tcp_data =None

    def cmdACCT(self):
        self.clientSocket.sendall(('ACCT '+self.account + Line_terminator).encode(codeType))
        account = self.clientSocket.recv(2048).decode(codeType)
        print(account)

    def cmdCDUP(self):
        print("####")
        self.clientSocket.sendall(('CDUP ' + Line_terminator).encode(codeType))
        CDUP = self.clientSocket.recv(2048).decode(codeType)
        print(CDUP)
        print("####")


    def cmdPASV(self):
        self.clientSocket.sendall(('PASV' + Line_terminator).encode(codeType))
        pasvResp = self.clientSocket.recv(2048).decode(codeType)
        print(pasvResp)
        print(type(pasvResp))
        self._tcp_IP, self._data_port = self.pasvModeStringHandling(pasvResp)
        print(self._tcp_IP," ",self._data_port)


    def cmdRETR(self, path):
        self.cmdPASV()
        self.createNewTCPConnection(self._data_port)
        self.clientSocket.sendall(('TYPE I'+Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response)
        self.clientSocket.sendall(('RETR' + ' '+ path+Line_terminator).encode(codeType))
        response2 = self.clientSocket.recv(8192).decode(codeType)
        print(response2)
        file = self._tcp_data.recv(8192)
        while 1:
            temp = self._tcp_data.recv(8192)
            if not temp:
                break
            file = file + temp
        print(self._tcp_data.recv(8192))
        f = open('hello.bin', "wb")
        f.write(file)
        f.close()
        response3 = self.clientSocket.recv(8192).decode(codeType)
        print(response3)
        self._tcp_data.close()


    def getResponseCode(self, message):
        code = message[:3]
        return int(code)

    def createNewTCPConnection(self, port):

        self._tcp_data = socket(AF_INET, SOCK_STREAM)
        self._tcp_data.connect((serverName, port))
        print('Data socket opened')
        # print("@@@@@")
        # responseMessage = self._tcp_data.recv(8192).decode(codeType)
        # print(responseMessage)


    def pasvModeStringHandling(self, server_resp):

        if ENTERING_PASV_MODE_CODE != self.getResponseCode(server_resp):
            return "Server did Not Respond"
        print(server_resp)


        print(type(server_resp))

        start_of_ip = server_resp.find('(')
        end_of_ip = server_resp.find(')')
        server_resp = server_resp[start_of_ip + 1:end_of_ip]
        server_resp = server_resp.split(',')
        # Retrieving IP from the server response
        # deliminating the IP by dot so as to get 192.134...

        temp = ''
        for i in range(0, 4):
            temp = temp + (server_resp[i]) + '.'

        server_ip = temp + server_resp[3]
        # Retrieving Port Number client must listen to

        # server_resp_port = server_resp[:end_of_ip]
        server_resp_port = server_resp[-2:]

        print(server_resp_port,'%%%%')
        # Formula to calculate port number
        self._data_port = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))
        print('Data Connection with IP: ' + server_ip + ':' + str(self._data_port))
        return server_ip, self._data_port




    # def activeLIST(self):





#  def login(self, username, password, account):

ftp = FTP_Client(serverName, serverPort, clientSocket)
ftp.login()
ftp.cmdPASV()
ftp.cmdLIST()
ftp.cmdPWD()
path = input("enter path")
ftp.cmdCWD(path)
ftp.cmdPASV()
ftp.cmdLIST()
path2 = input("Enter file to be downloaded")
ftp.cmdRETR(path2)


ftp.closeConnectcion()
