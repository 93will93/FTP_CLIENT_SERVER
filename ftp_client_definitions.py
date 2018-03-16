from socket import *
import time

serverName = '127.0.0.1'
# serverName = 'ftp.uconn.edu'
# serverName = "ftp.mirror.ac.za"
# serverName = 'elen4017.ug.eie.wits.ac.za'

serverPort = 21
clientSocket = socket(AF_INET, SOCK_STREAM)
codeType = "UTF-8"
Line_terminator = '\r\n'
ENTERING_PASV_MODE_CODE = 227

clientSocket.connect((serverName, serverPort))
print("Connected")
clientSocket.sendall(("YES").encode(codeType))

class FTP_Client:
    def __init__(self, servername, serverPort, clientSocket=None):
        self.serverName = servername
        self.serverPort = serverPort
        self.clientSocket = clientSocket
        # self.username = "anonymous"
        # self.password = "anonymous@"
        self.username = "test"
        self.password = "12345"

        self.account = ""
        self._data_port = None
        self._tcp_data = None
        self.Connect_Control_Socket(self.clientSocket)
        self._tcp_IP = None

    def Connect_Control_Socket(self, clientSocket):
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

    def cmdCWD(self, path):
        self.clientSocket.sendall(('CWD' + ' ' + path + Line_terminator).encode(codeType))
        cwd = self.clientSocket.recv(2048).decode(codeType)
        print(cwd)

    def cmdPWD(self):
        self.clientSocket.sendall(('PWD' + Line_terminator).encode(codeType))
        workingDirctory = self.clientSocket.recv(8192).decode(codeType)
        print(workingDirctory)

    def cmdLIST(self):
        self.cmdPASV()
        self.createNewTCPConnection(self._data_port)
        self.clientSocket.sendall(('List ' + Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response)
        list = self._tcp_data.recv(8192).decode(codeType)
        print(list)
        secondResponse = self.clientSocket.recv(8192).decode(codeType)
        print(secondResponse, '###')
        self._tcp_data.close()
        print("Data Socket closed")

        # self._tcp_data =None

    def cmdACCT(self):
        self.clientSocket.sendall(('ACCT ' + self.account + Line_terminator).encode(codeType))
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
        print(self._tcp_IP, " ", self._data_port)

    def cmdRETR(self, path):
        self.cmdPASV()
        self.createNewTCPConnection(self._data_port)
        self.clientSocket.sendall(('TYPE I' + Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response)
        self.clientSocket.sendall(('RETR' + ' ' + path + Line_terminator).encode(codeType))
        response2 = self.clientSocket.recv(8192).decode(codeType)
        print(response2)
        file = self._tcp_data.recv(8192)
        while 1:
            temp = self._tcp_data.recv(8192)
            if not temp:
                break
            file = file + temp
        f = open(path , "wb")
        f.write(file)
        f.close()
        response3 = self.clientSocket.recv(8192).decode(codeType)
        print(response3)
        self._tcp_data.close()

    def cmdSTOR(self, path):
        name = input("Enter File name to upload")
        fp = open(name, 'rb')
        self.cmdPASV()
        self.createNewTCPConnection(self._data_port)
        self.clientSocket.sendall(('TYPE I' + Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response, '@@@@@')

        self.clientSocket.sendall(('STOR' + ' ' + path + Line_terminator).encode(codeType))
        response2 = self.clientSocket.recv(8192).decode(codeType)
        print(response2, '!!!!!')

        data = fp.readline(8192)

        while 1:
            self._tcp_data.sendall(data)
            buf = fp.readline(8192)
            if not buf:
                break
            data = buf
        print("Awaiting Response")

        self._tcp_data.close()
        response3 = self.clientSocket.recv(8192).decode(codeType)
        print(response3)
        fp.close()

    def cmdMKD(self):
        path = input("Please ensure you are in the directory where the new sub-directory will be created, Enter new directory name: ")
        self.clientSocket.sendall(('MKD'+' ' + path + Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response)

    def cmdRMD(self):
        path = input("Please ensure you are in the directory where the old sub-directory will be deleted\n, Enter name of directory to be deleted:  ")
        self.clientSocket.sendall(('RMD' +' '+path + Line_terminator).encode(codeType))
        response = self.clientSocket.recv(8192).decode(codeType)
        print(response)

    def cmdDELE(self):
        path = input("Please insert the file name that you want to delete: ")
        print("Are you sure you want to delete", path, "?")
        doubleCheck = input("Please enter  'Yes' or 'No'")
        if doubleCheck == 'Yes':
            self.clientSocket.sendall(('DELE' +' ' +path + Line_terminator).encode(codeType))
            response = self.clientSocket.recv(8192).decode(codeType)
            print(response)
        elif doubleCheck == 'No':
            print("Nothing has been deleted")


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

        print(server_resp_port, '%%%%')
        # Formula to calculate port number
        self._data_port = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))
        print('Data Connection with IP: ' + server_ip + ':' + str(self._data_port))
        print("Data point", self._data_port)
        return server_ip, self._data_port


# ftp = FTP_Client(serverName, serverPort, clientSocket)
# ftp.login()
#
# while 1:
#     message = input("Enter command or 'Q' to quit session: ")
#
#     if message == "LIST":
#         ftp.cmdLIST()
#
#     if message == "PASV":
#         ftp.cmdPASV()
#
#     if message == "PWD":
#         ftp.cmdPWD()
#
#     if message == "CWD":
#         path = input("Enter path extentension")
#         ftp.cmdCWD(path)
#
#     if message == "RETR":
#         path = input("Enter file to download")
#         ftp.cmdRETR(path)
#
#     if message == "CDUP":
#         ftp.cmdCDUP()
#
#     if message == "Q":
#         break
#
#     if message == "STOR":
#         path = input("Enter path to upload")
#         ftp.cmdSTOR(path)
#
#     if message == 'MKD':
#         ftp.cmdMKD()
#
#     if message == 'RMD':
#         ftp.cmdRMD()
#
#     if message == 'DELE':
#         ftp.cmdDELE()
#
# ftp.closeConnectcion()
