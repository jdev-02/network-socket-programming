# CS3502 (Spring AY23) example UDP server 

from socket import *

serverPort = 12000

serverSocket = socket(AF_INET, SOCK_DGRAM)

serverSocket.bind(('', serverPort))  # '' is same as '0.0.0.0', meaning any NIC

print ("The server is ready to receive")

while True:
    print ("getting into the loop")

    # server being blocked calling recvfrom()
    message, clientAddress = serverSocket.recvfrom(2048)
           
    print ("received message:", message)
           
    modifiedMessage = message.decode().upper() # echo back all CAPS
    
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
