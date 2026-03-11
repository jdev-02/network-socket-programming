# CS3502 (Spring AY23) example UDP client 

from socket import *

serverName = '127.0.0.1'

serverPort = 12000

# binding to local IP and an available port > 1023
clientSocket = socket(AF_INET, SOCK_DGRAM)

message = input("Input lowercase sentence:")

print ("sending message: ", message)

clientSocket.sendto(message.encode(), (serverName, serverPort))

# blocking while receiving
buffer_size = 2048
modifiedMessage, serverAddress = clientSocket.recvfrom(buffer_size)

print ("received:", modifiedMessage.decode())

clientSocket.close()
