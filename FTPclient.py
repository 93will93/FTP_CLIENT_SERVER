import TCP


CRLF = '\r\n'
B_CRLF = b'\r\n'
FTP_PORT = 21
USER_LOGIN_SUCCESS = 230

class FTPclient:

    def __init__(self, ftp_server, user='', password=''):
        self._ftp_server = ftp_server
        self._user = user
        # self._password = password // We should probably not store user passwords
        self._tcp_cmd = TCP.TCP(self._ftp_server, FTP_PORT)
        self._welcome_msg = self._tcp_cmd.receive()
        print(self._welcome_msg)
        self.login(self._user, password, self._tcp_cmd)

    def login(self, user, password, sock):
        sock.transmit('USER' + user + CRLF)
        sock.transmit('PASS' + password + CRLF)
        server_resp = self._tcp_cmd.receive()
        print(server_resp)
        if str(USER_LOGIN_SUCCESS) == self.whatIsTheCode(server_resp):
            return True

        return False

    def whatIsTheCode(self, message):
        code = message[:3]
        return code


# Testing the class works with an open ftp server
if __name__ == '__main__':
    client = FTPclient('ftp.mirror.ac.za')
