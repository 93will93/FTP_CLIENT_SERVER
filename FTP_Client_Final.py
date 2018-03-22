import TCP_Client_Side
import socket

codeType = "UTF-8"
CRLF = '\r\n'
B_CRLF = b'\r\n'
SP = ' '

FTP_PORT = 12000
# localIP = '127.0.0.1'
#  Server response Codes
USER_LOGIN_SUCCESS_CODE = 230
ENTERING_PASV_MODE_CODE = 227
CWD_COMMAND_SUCCESSFUL = 250
BUFFERSIZE = 8192


class FTPclient:
    def __init__(self):
        self._ftp_server = ''
        self._user = ''
        self._working_dir = '/'
        self._server_response = ''
        self._welcome_message = ''

        self._data_port = None
        # TCP connections
        self._tcp_data = None
        self._tcp_cmd = None
        self.isOwnPort = False
        self.ownPort = None
        self.activeDataChannel = None


    def getServerMessage(self):
        return self._server_response

    def getWelcomeMessage(self):
        return self._welcome_message

    def login(self, ftp, user='', password=''):
        self._server_response = ''
        self._ftp_server = ftp
        self._user = user

        self._tcp_cmd = TCP_Client_Side.TCP(self._ftp_server, FTP_PORT ,True)
        s = str(self._tcp_cmd.receive())
        self._tcp_cmd.transmit('USER' + SP + user + CRLF)
        server_resp = self._tcp_cmd.receive()
        s += str(server_resp)
        self._tcp_cmd.transmit('PASS' + SP + password + CRLF)
        server_resp = self._tcp_cmd.receive()
        s += str(server_resp)
        self._server_response = s
        print(self._server_response)

        if USER_LOGIN_SUCCESS_CODE == self.whatIsTheCode(server_resp):
            return True

        return False

    def whatIsTheCode(self, message):
        code = message[:3]
        return int(code)

    def closeDataPort(self):
        print('Closing Data Port: ' + str(self._data_port))
        self._tcp_data.close()
        self._data_port = None

    def createDataPortConnection(self):
        self.pasv()

    def quit(self):
        self._tcp_cmd.transmit('QUIT' + CRLF)
        server_resp = self._tcp_cmd.receive()
        print(server_resp)

    def pasv(self):
        self.isOwnPort = False
        self._tcp_cmd.transmit('PASV' + SP + CRLF)
        server_resp = self._tcp_cmd.receive()
        print(str(server_resp))
        server_ip, self._data_port = self.pasvModeStringHandling(server_resp)
        self._tcp_data = TCP_Client_Side.TCP(self._ftp_server, self._data_port, True)
        return self._tcp_data

    def openActiveDataChannel(self):
        self.port()
        self.activeDataChannel = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.activeDataChannel.bind((serverIP, int(self.ownPort)))
        self.activeDataChannel.listen(1)

    def list(self):
        self._server_response = ''
        if self.isOwnPort == True:
            self.openActiveDataChannel()
            self._tcp_cmd.transmit('LIST' + SP + CRLF)
            self._server_response = self._tcp_cmd.receive()
            if self.whatIsTheCode(self._server_response) == 530:
                print('User not logged in, cannot access list')
                return
            print(self._server_response)
            self._server_response = self._tcp_cmd.receive()
            print(self._server_response)

            if(self.whatIsTheCode(self._server_response) == 425):
                print('Data connection was unsuccessful in creation')
                self.activeDataChannel.close()
                return

            activeDatasocket, activeSocketAdress = self.activeDataChannel.accept()
            print(activeSocketAdress)

            list = activeDatasocket.recv(8192).decode(codeType)
            while 1:
                temp = activeDatasocket.recv(8192).decode(codeType)
                if not temp:
                    break
                list = list + temp
            activeDatasocket.close()
            self.activeDataChannel.close()
            print(list)
            print('Closing Data Port: ' + str(self.ownPort))
        else:
            self.pasv()
            self._tcp_cmd.transmit('LIST' + SP + CRLF)
            self._server_response = self._tcp_cmd.receive()
            print(self._server_response)
            if self.whatIsTheCode(self._server_response) == 530:
                print('User not logged in, cannot access list')
                return
            self._server_response = self._tcp_cmd.receive()
            print(self._server_response)
            dataResponse = str(self._tcp_data.receive())
            print(dataResponse)
            self._tcp_data.close()
            print('Closing Data Port: ' + str(self._data_port))

    def retr(self, path):

        if self.isOwnPort == True:
            self.openActiveDataChannel()
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            print('Response to TYPE I: ' + str(self._tcp_cmd.receive(8192)))
            self._tcp_cmd.transmit('RETR' + SP + path + CRLF)
            print('Response to RETR: ' + str(self._tcp_cmd.receive()))
            activeDatasocket, activeSocketAdress = self.activeDataChannel.accept()
            data = activeDatasocket.recv(8192)
            while True:
                buffer = activeDatasocket.recv(8192)
                if not buffer:
                    break
                data += buffer
            f = open(path, "wb")
            f.write(data)
            f.close()
            response = self._tcp_cmd.receive()
            print(response)
            activeDatasocket.close()
            self.activeDataChannel.close()

        else:
            self.pasv()
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            print('Response to TYPE I: ' + str(self._tcp_cmd.receive(8192)))
            self._tcp_cmd.transmit('RETR' + SP + path + CRLF)
            print('Response to RETR: ' + str(self._tcp_cmd.receive()))

            data = self._tcp_data.receiveBinary()
            while True:
                buffer = self._tcp_data.receiveBinary()
                if not buffer:
                    break
                data += buffer

            print(str(self._tcp_data.receive(8192)))
            f = open(path, "wb")
            f.write(data)
            f.close()
            response3 = self._tcp_cmd.receive()
            print(response3)
            self.closeDataPort()

    def pwd(self):
        self._tcp_cmd.transmit('PWD' + CRLF)
        self._working_dir = self._tcp_cmd.receive()
        print(self._working_dir)

    def cwd(self, path):
        self._tcp_cmd.transmit('CWD' + SP + path + CRLF)
        server_response = self._tcp_cmd.receive()
        if CWD_COMMAND_SUCCESSFUL == self.whatIsTheCode(str(server_response)):
            self._working_dir += path
        print(server_response)

    def cdup(self):
        self._tcp_cmd.transmit('CDUP ' + CRLF)
        server_response = self._tcp_cmd.receive()
        print(server_response)

    def stor(self, path):
        if self.isOwnPort == True:

            self.openActiveDataChannel()
            name = input("Enter File name to upload: ")
            fp = open(name, 'rb')
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            response = self._tcp_cmd.receive()
            print(response)
            self._tcp_cmd.transmit('STOR' + SP + path + CRLF)
            response = self._tcp_cmd.receive()
            print(response)

            activeDatasocket, activeSocketAdress = self.activeDataChannel.accept()

            data = fp.readline(BUFFERSIZE)
            while True:
                activeDatasocket.sendall(data)
                buffer = fp.readline(BUFFERSIZE)
                if not buffer:
                    break
                data = buffer

            activeDatasocket.close()
            self.activeDataChannel.close()
            response = self._tcp_cmd.receive()
            print(response)
            fp.close()
        else:

            name = input("Enter File name to upload: ")
            fp = open(name, 'rb')
            self.pasv()
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            response = self._tcp_cmd.receive()
            print(response)

            self._tcp_cmd.transmit('STOR' + SP + path + CRLF)
            response = self._tcp_cmd.receive()
            print(response)

            data = fp.readline(BUFFERSIZE)

            while True:
                self._tcp_data.transmitAll(data)
                buffer = fp.readline(BUFFERSIZE)
                if not buffer:
                    break
                data = buffer

            self._tcp_data.close()
            response = self._tcp_cmd.receive(BUFFERSIZE)
            print(response)
            fp.close()

    def pasvModeStringHandling(self, server_resp):
        if ENTERING_PASV_MODE_CODE != self.whatIsTheCode(server_resp):
            return "Server did Not Respond"

        start_of_ip = server_resp.find('(')
        end_of_ip = server_resp.find(')')

        server_resp = server_resp[start_of_ip + 1:end_of_ip]

        server_resp = server_resp.split(',')
        temp = ''
        for i in range(0, 4):
            temp = temp + (server_resp[i]) + '.'

        server_ip = temp + server_resp[3]
        server_resp_port = server_resp[-2:]
        self._data_port = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))
        print('Data Connection with IP: ' + server_ip + ':' + str(self._data_port))
        return server_ip, self._data_port

    def mkd(self):
        path = input(
            "Please ensure you are in the directory where the new sub-directory will be created, Enter new directory name: ")
        self._tcp_cmd.transmit('MKD' + SP + path + CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def mode(self):
        modeCode = input('Enter MODE code, either "S", "B", "C": ')
        self._tcp_cmd.transmit('MODE' + SP + modeCode+ CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def stru(self):
        struCode = input('Enter File Structure "F", "R" or "P": ')
        self._tcp_cmd.transmit('STRU' + SP + struCode + CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def rmd(self):
        path = input(
            "Please ensure you are in the directory where the old sub-directory will be deleted\n, Enter name of directory to be deleted:  ")
        self._tcp_cmd.transmit('RMD' + SP + path + CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def dele(self):
        path = input("Please insert the file name that you want to delete: ")
        print("Are you sure you want to delete", path, "?")
        doubleCheck = input("Please enter  'Yes' or 'No'")
        doubleCheck = doubleCheck.upper()

        if doubleCheck == 'YES' or doubleCheck == 'Y':
            self._tcp_cmd.transmit('DELE' + SP + path + CRLF)
            response = self._tcp_cmd.receive()
            print(response)
        elif doubleCheck == 'No':
            print("Nothing has been deleted")

    def rnfr(self):
        path = input('Enter file that needs to be renamed: ')
        self._tcp_cmd.transmit('RNFR' + SP + path+ CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def rnto(self):
        newname = input('Enter the new name for the file: ')
        self._tcp_cmd.transmit('RNTO' +SP +newname +CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def noop(self):
        self._tcp_cmd.transmit('NOOP' + CRLF)
        print(self._tcp_cmd.receive())

    def syst(self):
        self._tcp_cmd.transmit('SYST' + CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    def help(self):
        self._tcp_cmd.transmit('HELP' + CRLF)
        data = self._tcp_cmd.receive()
        print(data)

    def port(self):
        self.isOwnPort = True
        port = input('Enter Port number wanting to be used for data connection: ')
        self.ownPort = int(port)
        serverHost = localIP.split('.')
        portRepresentation = [repr(self.ownPort // 256), repr(self.ownPort % 256)]
        portCommand = serverHost + portRepresentation
        cmdPORT = 'PORT ' + ','.join(portCommand)
        self._tcp_cmd.transmit(cmdPORT + CRLF)
        print(cmdPORT)
        response = self._tcp_cmd.receive()
        print(response)


# Testing the class works with an open ftp server
if __name__ == '__main__':

    eie_ftp = 'ELEN4017.ug.eie.wits.ac.za'
    eie_user = 'group14'
    eie_pass = 'engaqu4a'
    #
    mirror_ftp = 'ftp.mirror.ac.za'
    #
    # uccon_ftp = 'ftp.uconn.edu'
    uccon_user = 'anonymous'
    uccon_pass = 'anonymous@'
    #
    # localhost = 'localhost'
    localIP = '127.0.0.1'
    serverIP = '127.0.0.1'
    # localIP = mirror_ftp
    #
    # test_ftp = 'speedtest.tele2.net'

    client = FTPclient()
    # client.login(localIP, uccon_user, uccon_pass)
    client.login(serverIP, 'william', 'becerra')
    # client.login(eie_ftp, eie_user, eie_pass)
    # client = FTPclient(localhost, 'will', '')

    # client.pasv()
    # client.list()

    while 1:
        message = input('Enter command: ')
        message = message.upper()

        if message == "LIST":
            client.list()

        if message == "PASV":
            client.pasv()

        if message == "PWD":
            client.pwd()

        if message == "CWD":
            path = input("Enter path extension: ")
            client.cwd(path)

        if message == "RETR":
            path = input("Enter file to download: ")
            client.retr(path)

        if message == "CDUP":
            client.cdup()

        if message == 'STOR':
            path = input("Enter path extension: ")
            client.stor(path)

        if message == 'MKD':
            client.mkd()

        if message == 'RMD':
            client.rmd()

        if message == "Q" or message == 'QUIT':
            client.quit()
            break

        if message == 'DELE':
            client.dele()

        if message == 'NOOP':
            client.noop()

        if message == 'HELP':

            client.help()

        if message == 'PORT':
            client.port()

        if message == 'PASV':
            client.pasv()

        if message == 'MODE':
            client.mode()

        if message == 'STRU':
            client.stru()

        if message == 'SYST':
            client.syst()

        if message =='RNFR':
            client.rnfr()
            client.rnto()
