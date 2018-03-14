import socket

BUFFER_SIZE = 1024
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'


class TCP:
    def __init__(self, serverAdress, serverPort):
        self._serverAdress = serverAdress
        self._serverPort = serverPort
        self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add = (self._serverAdress, self._serverPort)
        self._clientSocket.connect(add)

    def transmit(self, s: object) -> object:
        self._clientSocket.send(s.encode(ENCODING_SCHEME))

    def __exit__(self):
        self._clientSocket.close()

    def receive(self, size=BUFFER_SIZE):
        serverResponse = self._clientSocket.recv(size).decode(ENCODING_SCHEME)
        return serverResponse

    def close(self):
        self._clientSocket.close()


if __name__ == '__main__':
    tcp = TCP(socket.gethostname(), 12005)
    tcp.transmit("Hello World!")
    Response = tcp.receive()
    print(str(Response))
