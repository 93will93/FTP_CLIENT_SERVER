self.cmdPASV()
self.createNewTCPConnection(self._data_port)
self.clientSocket.sendall(('TYPE I'+Line_terminator).encode(codeType))
response = self.clientSocket.recv(8192).decode(codeType)
print(response)
self.clientSocket.sendall(('RETR' + ' '+ path+Line_terminator).encode(codeType))
response2 = self.clientSocket.recv(8192).decode(codeType)
print(response2)
file = self._tcp_data.recv(8192)
while 1:
    temp = self._tcp_data.recv(8192)
    if not temp:
        break
    file = file + temp
print(self._tcp_data.recv(8192))
f = open('hello.bin', "wb")
f.write(file)
f.close()
response3 = self.clientSocket.recv(8192).decode(codeType)
print(response3)
self._tcp_data.close()


 def cmdPASV(self):
        self.clientSocket.sendall(('PASV' + Line_terminator).encode(codeType))
        pasvResp = self.clientSocket.recv(2048).decode(codeType)
        print(pasvResp)
        print(type(pasvResp))
        self._tcp_IP, self._data_port = self.pasvModeStringHandling(pasvResp)
        print(self._tcp_IP," ",self._data_port)


















