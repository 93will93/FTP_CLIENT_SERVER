# This script contains a Client GUI for an FTP server using pyQt and python3
# author: William Becerra Gonzalez
# author: Sailen Nair
#
# Networks Fundamentals ELEN4017
# University of the Witwatersrand
#


import socket

BUFFER_SIZE = 8192
BUFFER = ''
ENCODING_SCHEME = 'UTF-8'

#  This class abstracts the Networks Transport Layer. by creating TCP socket connections
# and functions for transmitting and reading to the socket
class TCP:
    # Class constructor, Requires an IP address and server port to bind a TCP socket
    def __init__(self, serverAdress, serverPort, passive):
        self._serverAdress = serverAdress
        self._serverPort = serverPort
        self._clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        add = (self._serverAdress, self._serverPort)
        if passive:
            self._clientSocket.connect(add)


        else:
            self._clientSocket.listen(1)

    # Transmitts the argument s to the TCP socket. Use utf-8 encoding
    def transmit(self, s: object) -> object:
        self._clientSocket.send(s.encode(ENCODING_SCHEME))

    # Transmitts the argument s to the TCP port. This function is used for data that's already encoded.
    def transmitAll(self, s):
        self._clientSocket.sendall(s)

    # Destructor to ensure that the TCP socket is closed and its not left binded.
    def __exit__(self):
        self.transmit('QUIT' + '\r\n')
        self._clientSocket.close()

    # Reads the TCP sockets buffer and decodes the data. Can use utf-8 encoding scheme or any other scheme defined by the argument
    def receive(self, size=BUFFER_SIZE, codec=ENCODING_SCHEME):
        serverResponse = self._clientSocket.recv(size).decode(codec)
        return serverResponse

    # receive binary data and returns it as binary.
    def receiveBinary(self):
        serverResponse = self._clientSocket.recv(BUFFER_SIZE)
        return serverResponse

    # Returns the socket
    def getSocket(self):
        return self._clientSocket
    # closes the TCP connection to be able to unbind the TCP port in use
    def close(self):
        self._clientSocket.close()




if __name__ == '__main__':
    tcp = TCP(socket.gethostname(), 12005)
    tcp.transmit("Hello World!")
    Response = tcp.receive()
    print(str(Response))

