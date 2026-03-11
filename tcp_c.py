# CS3502 (Spring AY23) example TCP client 

from socket import *

serverName = '127.0.0.1'

serverPort = 12000

# binding to local IP and an available port > 1023
clientSocket = socket(AF_INET, SOCK_STREAM)

print("trying to connect to server:", serverName, "port:", serverPort)
clientSocket.connect((serverName, serverPort))

message = input("Input lowercase sentence:")

print ("sending message: ", message)

clientSocket.send(message.encode())

# blocking while receiving
buffer_size = 2048

modifiedMessage = clientSocket.recv(buffer_size)

print ("received:", modifiedMessage.decode())

clientSocket.close()
