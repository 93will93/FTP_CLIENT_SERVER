from socket import *

serverName = "ftp.mirror.ac.za"
serverPort = 21

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

def Login():
    codeReturned = ''
    while codeReturned != "331 User Name 'OK'":
        username = input("USER")
        clientSocket.send(username.encode("UTF-8"))
        codeReturned = clientSocket.recv(2048).decode("UTF-8")
        print(codeReturned)

    passwordCodeReturned = ''
    while passwordCodeReturned != "230 User Logged in":
        password = input("PASS")
        clientSocket.send(password.encode("UTF-8"))
        passwordCodeReturned = clientSocket.recv(2048).decode("UTF-8")
        print(passwordCodeReturned)
    return


def PWD():
    code = "PWD"
    clientSocket.send(code.encode("UTF-8"))
    pwd = clientSocket.recv(2048).decode("UTF-8")
    print(pwd)


def close():
    closeMessage = "Ending user session"
    clientSocket.send(closeMessage.encode("UTF-8"))
    print(closeMessage)
    closeResonse = clientSocket.recv(2048).decode("UTF-8")
    print(closeResonse)
    closeClientSocket()


def closeClientSocket():
    clientSocket.close()


def DisplayCodesAvailable():
    print("PWD - print working directory")
    print("QUIT - close the connection")


welcomeMessage = clientSocket.recv(2048).decode('UTF-8')
print((welcomeMessage))

# Login()
#
# clientSocket.send("user test@gmail.com")
print("login succesful")
clientSocket.close()
#
#
#
# while 1:
#     code = input("code that is to be sent")
#     if code == "PWD":
#         PWD()
#
#     if code == "QUIT":
#         close()
#         break
#
#     if code == "display":
#         DisplayCodesAvailable()
#
#
# print("Session has ended")

