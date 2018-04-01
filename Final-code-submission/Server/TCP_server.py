'''
FTP Server TCP  Server
Authors: Sailen Nair (1078491) William Becerra (789146)
'''
import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'

'''
This class is for the TCP socket of the server, this is the socket that clients will 'knock' on to gain access
'''
class TCP:
    def __init__(self, serverAdress, serverPort):
        self._serverAdress = serverAdress
        self._serverPort = serverPort
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientSocket =None
        self._clientAddress = None

    def __exit__(self):
        self._serverSocket.close()

    # This function will listen for data connections
    def listen(self,amount):
        self._serverSocket.listen(amount)

    # This function will encode data and transmit
    def transmitAll(self, s):
        self._serverSocket.sendall(s.encode(ENCODING_SCHEME))

    # This function will accpet a connection
    def acceptConnection(self):
        self._clientSocket, self._clientAddress =  self._serverSocket.accept()

    def getServerSocket(self):
        return self._serverSocket

    def getServerAdress(self):
        return self._serverAdress

    def getClientSocket(self):
        return self._clientSocket

    def getClientAdress(self):
        return self._clientAddress

    # This function will bind the socket
    def bindSocket(self, address, port):
        self._serverSocket.bind(("", port))

    def close(self):
        self._serverSocket.close()
