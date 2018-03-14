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
        self._clientSocket.sendall(s.encode(ENCODING_SCHEME))

    def __exit__(self):
        self._clientSocket.close()

    def receive(self):
        serverResponse = self._clientSocket.recv(BUFFER_SIZE).decode(ENCODING_SCHEME)
        return serverResponse


if __name__ == '__main__':
    tcp = TCP(socket.gethostname(), 12005)
    tcp.transmit("Hello World!")
    Response = tcp.receive()
    print(str(Response))