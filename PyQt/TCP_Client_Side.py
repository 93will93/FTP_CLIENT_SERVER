import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'


class TCP:
    def __init__(self, serverAdress, serverPort, passive):
        self._serverAdress = serverAdress
        self._serverPort = serverPort
        self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add = (self._serverAdress, self._serverPort)
        if passive:
            self._clientSocket.connect(add)


        else:
            self._clientSocket.listen(1)


    def transmit(self, s: object) -> object:
        self._clientSocket.send(s.encode(ENCODING_SCHEME))

    def transmitAll(self, s):
        self._clientSocket.sendall(s)

    def __exit__(self):
        self.transmit('QUIT' + '\r\n')
        self._clientSocket.close()

    def receive(self, size=BUFFER_SIZE, codec=ENCODING_SCHEME):
        serverResponse = self._clientSocket.recv(size).decode(codec)
        return serverResponse

    def receiveBinary(self):
        serverResponse = self._clientSocket.recv(BUFFER_SIZE)
        return serverResponse

    def getSocket(self):
        return self._clientSocket

    def close(self):
        self._clientSocket.close()




if __name__ == '__main__':
    tcp = TCP(socket.gethostname(), 12005)
    tcp.transmit("Hello World!")
    Response = tcp.receive()
    print(str(Response))

