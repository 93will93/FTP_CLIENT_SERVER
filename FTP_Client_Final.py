import TCP_Client_Side

CRLF = '\r\n'
B_CRLF = b'\r\n'
SP = ' '

FTP_PORT = 21
localIP = '127.0.0.1'
#  Server response Codes
USER_LOGIN_SUCCESS_CODE = 230
ENTERING_PASV_MODE_CODE = 227
CWD_COMMAND_SUCCESSFUL = 250


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

    def getServerMessage(self):
        return self._server_response

    def getWelcomeMessage(self):
        return self._welcome_message

    def login(self, ftp, user='', password=''):
        self._server_response = ''
        self._ftp_server = ftp
        self._user = user

        self._tcp_cmd = TCP_Client_Side.TCP(self._ftp_server, FTP_PORT)
        s = str(self._tcp_cmd.receive())
        self._tcp_cmd.transmit('USER' + SP + user + CRLF)
        server_resp = self._tcp_cmd.receive()
        s += str(server_resp)
        self._tcp_cmd.transmit('PASS' + SP + password + CRLF)
        server_resp = self._tcp_cmd.receive(8192)
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
        self._tcp_cmd.transmit('PASV' + SP + CRLF)
        server_resp = self._tcp_cmd.receive()
        print(str(server_resp))
        server_ip, self._data_port = self.pasvModeStringHandling(server_resp)
        self._tcp_data = TCP_Client_Side.TCP(self._ftp_server, self._data_port)
        return self._tcp_data

    def list(self):
        self._server_response = ''
        self.pasv()
        self._tcp_cmd.transmit('LIST' + SP + CRLF)
        self._server_response = str(self._tcp_cmd.receive())
        self._server_response += str(self._tcp_cmd.receive())
        # print(self._tcp_cmd.receive())
        # print(self._tcp_cmd.receive())

        self._server_response += str(self._tcp_data.receive())
        print(self._server_response)
        self._tcp_data.close()
        print('Closing Data Port: ' + str(self._data_port))

    def retr(self, path):
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
        # self.createDataPortConnection()
        self._tcp_cmd.transmit('PWD' + CRLF)
        self._working_dir = self._tcp_cmd.receive()
        # print('Here ' + self._tcp_cmd.receive())
        # self._working_dir = self._tcp_data.receive()
        # self.closeDataPort()
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
        name = input("Enter File name to upload: ")
        fp = open(name, 'rb')
        self.pasv()
        self._tcp_cmd.transmit('TYPE I' + CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response, '@@@@@')

        self._tcp_cmd.transmit('STOR' + SP + path + CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response + '!!!!!')

        data = fp.readline(8192)

        while True:
            self._tcp_data.transmitAll(data)
            buffer = fp.readline(8192)
            if not buffer:
                break
            data = buffer

        print("Awaiting Response")

        self._tcp_data.close()
        response = self._tcp_cmd.receive(8192)
        print(response)
        fp.close()

    def pasvModeStringHandling(self, server_resp):
        if self.isOwnPort == True:
            self._data_port = int(self.ownPort)
            return '127.0.0.1', self._data_port
        else:
            if ENTERING_PASV_MODE_CODE != self.whatIsTheCode(server_resp):
                return "Server did Not Respond"

            start_of_ip = server_resp.find('(')
            end_of_ip = server_resp.find(')')

            server_resp = server_resp[start_of_ip + 1:end_of_ip]
            # server_resp = server_resp[:end_of_ip]

            server_resp = server_resp.split(',')

            # Retrieving IP from the server response
            # deliminating the IP by dot so as to get 192.134...
            temp = ''
            for i in range(0, 4):
                temp = temp + (server_resp[i]) + '.'

            server_ip = temp + server_resp[3]
            # Retrieving Port Number client must listen to
            server_resp_port = server_resp[-2:]
            # Formula to calculate port number
            self._data_port = int((int(server_resp_port[0]) * 256) + int(server_resp_port[1]))
            print('Data Connection with IP: ' + server_ip + ':' + str(self._data_port))
            return server_ip, self._data_port

    def mkd(self):
        path = input(
            "Please ensure you are in the directory where the new sub-directory will be created, Enter new directory name: ")
        self._tcp_cmd.transmit('MKD' + SP + path + CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response)

    def rmd(self):
        path = input(
            "Please ensure you are in the directory where the old sub-directory will be deleted\n, Enter name of directory to be deleted:  ")
        self._tcp_cmd.transmit('RMD' + SP + path + CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response)

    def dele(self):
        path = input("Please insert the file name that you want to delete: ")
        print("Are you sure you want to delete", path, "?")
        doubleCheck = input("Please enter  'Yes' or 'No'")
        doubleCheck = doubleCheck.upper()

        if doubleCheck == 'YES' or doubleCheck == 'Y':
            self._tcp_cmd.transmit('DELE' + SP + path + CRLF)
            response = self._tcp_cmd.receive(8192)
            print(response)
        elif doubleCheck == 'No':
            print("Nothing has been deleted")

    def noop(self):
        self._tcp_cmd.transmit('NOOP' + CRLF)
        print(self._tcp_cmd.receive())

    def help(self, about=''):
        self.pasv()
        self._tcp_cmd.transmit('HELP' + SP + CRLF)
        print(self._tcp_cmd.receive())
        dat = ''
        while True:
            buf = self._tcp_cmd.receive()
            if not buf:
                break
            dat += buf
        print(dat)
        self._tcp_data.close()
        print(dat)

    # Just need to fix how the port number is either transmitted or recieved, it has
    # a specific format
    def port(self):
        self.isOwnPort = True
        port = input('Enter Port number wanting to be used for data connection: ')
        self.ownPort = int(port)
        serverHost = localIP.split('.')
        portRepresentation = [repr(self.ownPort // 256), repr(self.ownPort % 256)]
        portCommand = serverHost+portRepresentation
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

    mirror_ftp = 'ftp.mirror.ac.za'

    uccon_ftp = 'ftp.uconn.edu'
    uccon_user = 'anonymous'
    uccon_pass = 'anonymous@'

    localhost = 'localhost'
    localIP = '127.0.0.1'

    test_ftp = 'speedtest.tele2.net'

    client = FTPclient()
    client.login(localhost, 'test', '12345')
    # client = FTPclient(eie_ftp, eie_user, eie_pass)
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
            x = input('What do you need help on: ')
            client.help(x)

        if message == 'PORT':
            client.port()
