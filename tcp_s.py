# CS3502 (Spring AY23) example TCP server 

from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_STREAM)

serverSocket.bind(('', serverPort))  # '' is same as '0.0.0.0', meaning any NIC

serverSocket.listen() # activate server socket to listen for new connections

print ("The server is listening for new connection....")

while True:

    # server blocked calling accept(), i.e., waiting for new client connects
    connectionSocket, clientAddress = serverSocket.accept()
           
    print ("connected with a new client:", clientAddress)

    # server blocked calling recv() 
    message = connectionSocket.recv(1024)
           
    modifiedMessage = message.decode().upper() # echo back all CAPS
    connectionSocket.send(modifiedMessage.encode())

    connectionSocket.close() # close connection to this client
