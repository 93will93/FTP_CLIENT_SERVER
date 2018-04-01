# This script contains a Client command line application for an FTP server using pyQt and python3
# author: William Becerra Gonzalez
# author: Sailen Nair
#
# Networks Fundamentals ELEN4017
# University of the Witwatersrand
#

import TCP_Client_Side
import socket
codeType = "UTF-8"
CRLF = '\r\n'
B_CRLF = b'\r\n'
SP = ' '

FTP_PORT = 21
# localIP = '127.0.0.1'
#  Server response Codes
USER_LOGIN_SUCCESS_CODE = 230
ENTERING_PASV_MODE_CODE = 227
CWD_COMMAND_SUCCESSFUL = 250

# This class contains the back end of a FTP client application. This application is command line requiring the user to
# input the necessery FTP command to send to the server.

class FTPclient:
    # Class constructor. Defines the initial states of the class invariants
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

    # Returns the las message the server responds to the client
    def getServerMessage(self):
        return self._server_response

    # This function handles the user login to an ftp server defined by ftp
    # it takes the optional arguments user and password.
    # It returns true if the login was succesfull
    def login(self, ftp, user='', password=''):
        self._server_response = ''
        self._ftp_server = ftp
        self._user = user

        self._tcp_cmd = TCP_Client_Side.TCP(self._ftp_server, FTP_PORT, True)
        s = str(self._tcp_cmd.receive())
        self._tcp_cmd.transmit('USER' + SP + user + CRLF)
        server_resp = self._tcp_cmd.receive()
        s += str(server_resp)
        self._tcp_cmd.transmit('PASS' + SP + password + CRLF)
        server_resp = self._tcp_cmd.receive(8192)
        s += str(server_resp)
        self._server_response = s
        # print(self._server_response)

        if USER_LOGIN_SUCCESS_CODE == self.whatIsTheCode(server_resp):
            return True

        return False

    # This function extracts the server reply code from the whole server reply message.
    # It takes in as an argument the server reply message and it returns the reply code.
    def whatIsTheCode(self, message):
        code = message[:3]
        return int(code)

    # This function closes the data port. It is used after a data transfer operation is complete.
    def closeDataPort(self):
        # print('Closing Data Port: ' + str(self._data_port))
        self._tcp_data.close()
        self._data_port = None

    #  Creates a Data Port connection by entering Passive mode.
    def createDataPortConnection(self):
        self.pasv()

    # Sends the QUIT command to the server
    def quit(self):
        self._server_response = ''
        self._tcp_cmd.transmit('QUIT' + CRLF)
        self._server_response = self._tcp_cmd.receive()

    # Sends the PASV command to the server and handles all server reply codes to enter Passive Mode.
    # The function returns the Data Part Number created for the data connection
    def pasv(self):
        self.isOwnPort = False
        self._tcp_cmd.transmit('PASV' + SP + CRLF)
        server_resp = self._tcp_cmd.receive()
        self._server_response += server_resp
        server_ip, self._data_port = self.pasvModeStringHandling(server_resp)
        self._tcp_data = TCP_Client_Side.TCP(self._ftp_server, self._data_port, True)
        return self._tcp_data

    # Sends the List command to the server. It handles all the server reply codes to store the list in the
    # self._server_message variable. The function supports Active and Passive mode
    def list(self):
        self._server_response = ''
        if self.isOwnPort:
            # dataSock = self.activePortSocket()
            self.port()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((localIP, int(self.ownPort)))
            sock.listen(1)

            self._tcp_cmd.transmit('LIST' + SP + CRLF)
            self._server_response += self._tcp_cmd.receive()
            self._server_response += self._tcp_cmd.receive()
            self._server_response += self._tcp_cmd.receive()

            if self.whatIsTheCode(self._server_response) == 425:
                print('Data connection was unsuccessful in creation')
                sock.close()
                return

            activeDatasocket, activeSocketAdress = sock.accept()

            list = activeDatasocket.recv(8192).decode(codeType)
            while 1:
                temp = activeDatasocket.recv(8192).decode(codeType)
                if not temp:
                    break
                list = list + temp
            activeDatasocket.close()
            sock.close()

        else:
            self.pasv()
            self._tcp_cmd.transmit('LIST' + SP + CRLF)
            self._server_response += self._tcp_cmd.receive()
            self._server_response += self._tcp_cmd.receive()
            self._server_response += self._tcp_data.receive()
            self._tcp_data.close()

    # Sends the RETR command to the server. This informs the server the user intends to retrieve a file defined
    # by  the argument file_to_download and it stores the file locally in the directory defined by the path argument.
    def retr(self, file_to_download, path=''):
        self._server_response = ''
        if self.isOwnPort == True:
            self.port()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((localIP, int(self.ownPort)))
            sock.listen(1)
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            self._server_response += self._tcp_cmd.receive(8192)
            self._tcp_cmd.transmit('RETR' + SP + file_to_download + CRLF)
            self._server_response += self._tcp_cmd.receive()

            activeDatasocket, activeSocketAdress = sock.accept()
            data = activeDatasocket.recv(8192)
            while True:
                buffer = activeDatasocket.recv(8192)
                if not buffer:
                    break
                data += buffer
            if path == '':
                path += file_to_download

            f = open(path, "wb")
            f.write(data)
            f.close()
            self._server_response += self._tcp_cmd.receive()
            activeDatasocket.close()

        else:
            self.pasv()
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            self._server_response += self._tcp_cmd.receive(8192)
            self._tcp_cmd.transmit('RETR' + SP + file_to_download + CRLF)
            self._server_response += self._tcp_cmd.receive()

            data = self._tcp_data.receiveBinary()
            while True:
                buffer = self._tcp_data.receiveBinary()
                if not buffer:
                    break
                data += buffer

            print(str(self._tcp_data.receive(8192)))
            if path == '':
                path += file_to_download

            f = open(path, "wb")
            f.write(data)
            f.close()
            self._server_response += self._tcp_cmd.receive()
            self.closeDataPort()

    # This function ends the PWD command to the server and stores the server reply message in the self._server_message
    # variable
    def pwd(self):
        # self.createDataPortConnection()
        self._tcp_cmd.transmit('PWD' + CRLF)
        self._working_dir = self._tcp_cmd.receive()
        print(self._working_dir)

    # Sends the CWD command to the FTP server. It handles all server communication to allow the user to change
    # the working directory to the path defined by the argument path
    def cwd(self, path):
        self._server_response = ''
        self._tcp_cmd.transmit('CWD' + SP + path + CRLF)
        server_response = self._tcp_cmd.receive()
        self._server_response += server_response
        if CWD_COMMAND_SUCCESSFUL == self.whatIsTheCode(str(server_response)):
            self._working_dir += path

    # Sends the CDUP command to the TP server. It handles all server communication to allow the user to
    # move to the parent directory of the current working directory
    def cdup(self):
        self._tcp_cmd.transmit('CDUP ' + CRLF)
        self._server_response += self._tcp_cmd.receive()
        self._server_response += '\n'

    # Sends the STOR command to the FTP server. This command allows the user to upload a file to the server.
    # The function takes in as argument the name of the file to be uploaded and the path on the server
    # for the file to be uploaded
    def stor(self, path, name=''):
        self._server_response = ''
        if self.isOwnPort:
            self.port()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((localIP, int(self.ownPort)))
            sock.listen(1)
            fp = open(name, 'rb')
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            response = self._tcp_cmd.receive(8192)
            self._tcp_cmd.transmit('STOR' + SP + path + CRLF)
            response += self._tcp_cmd.receive(8192)
            activeDatasocket, activeSocketAdress = sock.accept()
            data = fp.readline(8192)

            while True:
                activeDatasocket.sendall(data)
                buffer = fp.readline(8192)
                if not buffer:
                    break
                data = buffer

            print("Awaiting Response")

            activeDatasocket.close()
            response += self._tcp_cmd.receive(8192)
            self._server_response += response
            print(response)
            fp.close()
        else:
            fp = open(name, 'rb')
            self.pasv()
            self._tcp_cmd.transmit('TYPE I' + CRLF)
            self._server_response += self._tcp_cmd.receive(8192)

            self._tcp_cmd.transmit('STOR' + SP + path + CRLF)
            self._server_response += self._tcp_cmd.receive(8192)

            data = fp.readline(8192)

            while True:
                self._tcp_data.transmitAll(data)
                buffer = fp.readline(8192)
                if not buffer:
                    break
                data = buffer

            self._tcp_data.close()
            self._server_response += self._tcp_cmd.receive(8192)
            fp.close()

    # Handles the server response string to be able to extract the port number established for passive mode
    # It takes as an argument the server response to a passive mode connection adn returns the server ip and
    # port number for the data transfer
    def pasvModeStringHandling(self, server_resp):
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
        return server_ip, self._data_port

    # Sends MKD command to the server. Allow the user to make a new directory in the server defined by the path argument.
    def mkd(self, path):
        self._server_response = ''
        self._tcp_cmd.transmit('MKD' + SP + path + CRLF)
        self._server_response += self._tcp_cmd.receive(8192)

    # Sends the MODE command to the server. Prompts the user to input the mode.
    def mode(self):
        modeCode = input('Enter MODE code, either "S", "B", "C": ')
        self._tcp_cmd.transmit('MODE' + SP + modeCode+ CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response)

    # Sends the structure command to the server. Prompts the user for the structure
    def stru(self):
        struCode = input('Enter File Structure "F", "R" or "P": ')
        self._tcp_cmd.transmit('STRU' + SP + struCode + CRLF)
        response = self._tcp_cmd.receive(8192)
        print(response)

    # Sends the RMD command to the server. This command allows user to remove a folder in the server
    def rmd(self, path):
        self._server_response = ''
        self._tcp_cmd.transmit('RMD' + SP + path + CRLF)
        self._server_response += self._tcp_cmd.receive(8192)
    # Sends the DELE command to the server. This command is used to delete a file in the server
    def dele(self, path):
        self._server_response = ''
        self._tcp_cmd.transmit('DELE' + SP + path + CRLF)
        self._server_response += self._tcp_cmd.receive(8192)

    # Sends the RNFR command to the server.
    # Rename from command allows the user to rename a file and it should be followed by rnto() function
    def rnfr(self):
        path = input('Enter file that needs to be renamed: ')
        self._tcp_cmd.transmit('RNFR' + SP + path+ CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    # Sends the RNTO command to the server.
    # Rename to command renames a file to a new name. It should be preceded by the rnfr() function
    def rnto(self):
        newname = input('Enter the new name for the file: ')
        self._tcp_cmd.transmit('RNTO' +SP +newname +CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    # Sends the NOOP command to the server.
    # The No Operation command for the user to request an OK reply from the server
    def noop(self):
        self._tcp_cmd.transmit('NOOP' + CRLF)
        print(self._tcp_cmd.receive())

    # Sends the SYST command to the server
    def syst(self):
        self._tcp_cmd.transmit('SYST' + CRLF)
        response = self._tcp_cmd.receive()
        print(response)

    # Sends the HELP command to the server
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

    # Sends the PORT command to the server. This is use for active mode connection.
    # Prompts the user for a port number and tells the server the port number for the data connection
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


# This is the main loop for the main command line application
# The user is prompeted for an FTP command defined in RFC 959
# The user can enter the command in upper or lower case.
if __name__ == '__main__':

    # eie_ftp = 'ELEN4017.ug.eie.wits.ac.za'
    # eie_user = 'group14'
    # eie_pass = 'engaqu4a'
    #
    mirror_ftp = 'ftp.mirror.ac.za'
    #
    # uccon_ftp = 'ftp.uconn.edu'
    uccon_user = 'anonymous'
    uccon_pass = 'anonymous@'
    #
    # localhost = 'localhost'
    localIP = '127.0.0.1'
    # localIP = mirror_ftp
    #
    # test_ftp = 'speedtest.tele2.net'

    client = FTPclient()
    # client.login(localIP, uccon_user, uccon_pass)
    client.login('127.0.0.1', 'will', '1010')
    # client = FTPclient(eie_ftp, eie_user, eie_pass)
    # client = FTPclient(localhost, 'will', '')

    # client.pasv()
    # client.list()

    while 1:
        message = input('Enter command: ')
        message = message.upper()

        if message == "LIST":
            client.list()
            print(client.getServerMessage())

        if message == "PASV":
            client.pasv()
            print(client.getServerMessage())

        if message == "PWD":
            client.pwd()
            print(client.getServerMessage())

        if message == "CWD":
            path = input("Enter path extension: ")
            client.cwd(path)
            print(client.getServerMessage())

        if message == "RETR":
            path = input("Enter file to download: ")
            client.retr(path)
            print(client.getServerMessage())

        if message == "CDUP":
            client.cdup()
            print(client.getServerMessage())

        if message == 'STOR':
            path = input("Enter path extension: ")
            client.stor(path)
            print(client.getServerMessage())

        if message == 'MKD':
            path = input("Enter File Name: ")
            client.mkd(path)
            print(client.getServerMessage())

        if message == 'RMD':
            path = input("Enter Folder to be removed: ")
            client.rmd(path)
            print(client.getServerMessage())

        if message == "Q" or message == 'QUIT':
            client.quit()
            print(client.getServerMessage())
            break

        if message == 'DELE':
            path = input("Enter File name: ")
            client.dele(path)
            print(client.getServerMessage())

        if message == 'NOOP':
            client.noop()

        if message == 'HELP':
            x = input('What do you need help on: ')
            client.help(x)

        if message == 'PORT':
            client.port()

        if message == 'PASV':
            client.pasv()
            print(client.getServerMessage())

        if message == 'MODE':
            client.mode()

        if message == 'STRU':
            client.stru()

        if message == 'SYST':
            client.syst()

        if message =='RNFR':
            client.rnfr()
            client.rnto()
