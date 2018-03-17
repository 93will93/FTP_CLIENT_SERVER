import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'


class TCP:
    def __init__(self, serverSocket,clientSocket, clientAdress):

        self._serverSocket = serverSocket
        self._clientAddress = clientAdress
        self._clientSocket = clientSocket
        # self.transmitAll("welcome")

    def transmit(self, s: object) -> object:
        self._clientSocket.send(s.encode(ENCODING_SCHEME))

    def transmitAll(self, s):
        self._clientSocket.sendall(s.encode(ENCODING_SCHEME))

    def __exit__(self):
        self.transmit('Closing socket' + '\r\n')
        self._clientSocket.close()

    def receive(self, size=BUFFER_SIZE, codec=ENCODING_SCHEME):
        clientResponse = self._clientSocket.recv(size).decode(codec)
        return clientResponse

    def acceptConnection(self):
        self._clientSocket, self._clientAddress =  self._serverSocket.accept()

    def close(self):
        self._clientSocket.close()

    def getSocket(self):
        return self._clientSocket

    def getAdress(self):
        return self._clientAddress

# if __name__ == '__main__':
#     tcp = TCP(socket.gethostname(), 12005)
#     tcp.transmit("Hello World!")
#     Response = tcp.receive()
#     print(str(Response))