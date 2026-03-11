#[author]
#CS3502 Computer Communications and Networks Lab 1
#Professor Xie

'''
-planning
-server:
-parse game_time from cmd line, bind to fixed port, generate the rand num(1,100), 
-accept client connection, then start game time countdown
-when game_time is up, send the echo message of what client put in and the rand num
'''

# CS3502 (Spring AY23) example TCP server (regular socket calls)

from socket import *                             
from random import *
import argparse

HOST = ''                                 #listen on all interfaces
PORT = 13000                                     

def parse_args():
    '''returns parsed value of game_time'''
    parser = argparse.ArgumentParser(description='This program starts the TCP server with the option for game time in seconds')
    parser.add_argument('--game_time', type=int, required=True)
    args = parser.parse_args()
    if args.game_time <= 0:
        parser.error("game_time option must be a postitive integer")
    return args.game_time

def socket_setup(host, port):
    '''standard socket setup code for tcp'''
    serverSocket = socket(AF_INET, SOCK_STREAM)          #create a TCP socket (reliable, ordered byte stream)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #allow quick rebinding after a crash or restart of the server
    serverSocket.bind((host, port))                      #associate the socket with (ip, port) so clients can connect
    serverSocket.listen(1)                               #put into passive mode to accept incoming connections
    return serverSocket

def recv_line(conn):                             
    """Read bytes from a TCP stream until '\n' is seen or the peer closes.
       Returns a decoded string without the trailing '\n', or None on EOF before any byte."""
    buf = bytearray()                            #accumulate bytes here (TCP can split/merge sends arbitrarily)
    while True:
        chunk = conn.recv(4096)                  #blocking read from the TCP stream (up to 4096 bytes)
        if not chunk:                            #empty chunk => peer closed connection (EOF)
            if not buf:                          #no data accumulated -> treat as None (caller can break)
                return None
            break                                #some data without '\n' then EOF -> we'll return it as a line
        buf.extend(chunk)                        #append newly received bytes
        if b'\n' in chunk:                       #our line delimiter is present somewhere in the buffer
            break
    line, _, _rest = bytes(buf).partition(b'\n')
    return line.decode()                         #bytes -> str

def play_single_player_game(connectionSocket, answer, game_time):
    connectionSocket.settimeout(game_time)
    try:
        line = recv_line(connectionSocket)
        if line is not None:
            guess = int(line)
        else:
            guess = None
    except TimeoutError:
        guess = None #no guess received from client program
    if guess is not None:
        if guess == answer:
            message = f"Congratulations, your guess of {guess} matches the answer of {answer}\n"
        else:
            message = f"Sorry, your guess of {guess} did not match the correct answer of {answer}\n"
    else:
        message = f"Time's up! You did not send a guess before the game time ran up. The answer was {answer}\n"
    
    connectionSocket.sendall(message.encode())
    connectionSocket.close()

def main():
    game_time = parse_args()
    serverSocket = socket_setup(HOST, PORT)
    answer = randint(1, 100)
    print(f"TCP server ready on {HOST}:{PORT}")
    
    try:
        connectionSocket, clientAddress = serverSocket.accept()
        print("TCP connection from:", clientAddress)
        play_single_player_game(connectionSocket, answer, game_time)
    finally:
        serverSocket.close()
    print("Game complete. Server exiting...")
if __name__ == "__main__":
    main()
