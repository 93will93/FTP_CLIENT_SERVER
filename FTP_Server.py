import os
from socket import *
import time


serverPort = 12000
serverHost = gethostname()
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))

serverSocket.listen(5)
connectionSocket, addr = serverSocket.accept()
#messageRecieved = connectionSocket.recv(2048)


def login():

    username = connectionSocket.recv(2048).decode("UTF-8")

    while 1:
        if username == "sailen":
            connectionSocket.send(("331 User Name 'OK'").encode("UTF-8"))
            break
        else:
            connectionSocket.send(("404 User name incorrect").encode("UTF-8"))
            username = connectionSocket.recv(2048).decode("UTF-8")

    password = connectionSocket.recv(2048).decode("UTF-8")

    while 1:
        if password =="12345":
            connectionSocket.send(("230 User Logged in").encode("UTF-8"))
            break
        else:
            connectionSocket.send(("404 Incorrect Password").encode("UTF-8"))
            password = connectionSocket.recv(2048).decode("UTF-8")
    print("You have logged in successfully")


def pwd():
    connectionSocket.send(os.getcwd().encode("UTF-8"))


def close():
    closeResponse = "200 OK"
    closeMessage = connectionSocket.recv(2048).decode("UTF-8")
    print(closeMessage)

    connectionSocket.send(closeResponse.encode("UTF-8"))
    print(closeResponse)


login()
messageCode = connectionSocket.recv(2048).decode("UTF-8")
while 1:
    print(messageCode)
    if messageCode == "PWD":
         pwd()
    if messageCode == "QUIT":
        close()
    messageCode = connectionSocket.recv(2048).decode("UTF-8")
