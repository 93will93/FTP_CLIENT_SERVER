'''
FTP Server TCP Client for Server
Authors: Sailen Nair (1078491) William Becerra (789146)
'''

import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'

'''
This is the TCP class for the client connection within the server, it only handles the control connection
'''
class TCP:
    def __init__(self, serverSocket,clientSocket, clientAdress):

        self._serverSocket = serverSocket
        self._clientAddress = clientAdress
        self._clientSocket = clientSocket

    # This function will encode the data and transmit it to the client.
    def transmit(self, s: object) -> object:
        self._clientSocket.send(s.encode(ENCODING_SCHEME))

    def transmitAll(self, s):
        self._clientSocket.sendall(s.encode(ENCODING_SCHEME))

    def __exit__(self):
        self.transmit('Closing socket' + '\r\n')
        self._clientSocket.close()

    # This fucntion will recieve the data and decode it
    def receive(self, size=BUFFER_SIZE, codec=ENCODING_SCHEME):
        clientResponse = self._clientSocket.recv(size).decode(codec)
        return clientResponse

    # This function will accept the connection from the client.
    def acceptConnection(self):
        self._clientSocket, self._clientAddress =  self._serverSocket.accept()

    def close(self):
        self._clientSocket.close()

    def getSocket(self):
        return self._clientSocket

    def getAdress(self):
        return self._clientAddress
