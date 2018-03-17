import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'


class TCP:
    def __init__(self, serverAdress, serverPort):
        self._serverAdress = serverAdress
        self._serverPort = serverPort
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._clientSocket =None
        self._clientAddress = None
        # self._serverSocket.bind(('', self._serverPort))


        # self._clientAddress = None
        # self._clientSocket = None

    # def transmit(self, s: object) -> object:
    #     self._clientSocket.send(s.encode(ENCODING_SCHEME))
    #
    # def transmitAll(self, s):
    #     self._clientSocket.sendall(s)

    def __exit__(self):
        # self.transmit('QUIT' + '\r\n')
        self._serverSocket.close()

    # def receive(self, size=BUFFER_SIZE, codec=ENCODING_SCHEME):
    #     serverResponse = self._clientSocket.recv(size).decode(codec)
    #     return serverResponse

    def listen(self,amount):
        self._serverSocket.listen(amount)

    # def acceptConnection(self):
    #     self._clientSocket, self._clientAddress =  self._serverSocket.accept()

    # def closeClient(self):
    #     if self._clientSocket != None:
    #         self._clientSocket.close()

    def transmitAll(self, s):
        self._serverSocket.sendall(s.encode(ENCODING_SCHEME))

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

    def bindSocket(self, address, port):
        self._serverSocket.bind((address, port))



    def close(self):
        self._serverSocket.close()



# if __name__ == '__main__':
#     tcp = TCP(socket.gethostname(), 12005)
#     tcp.transmit("Hello World!")
#     Response = tcp.receive()
#     print(str(Response))