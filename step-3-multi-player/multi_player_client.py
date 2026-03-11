#Jonathan Goohs
#CS3502 Computer Communications and Networks Lab 1
#Professor Xie

'''
-planning
-client:
-startup of program with cmd line option for the ip addr (need to validate parsing of this)
-connect to server:port via handshake
-prompt user for guess, send guess to server, wait for response after game_time ends from server

'''

from socket import *
import argparse

PORT = 13000

def parse_args():
    '''parser the server ip address and returns for connection to server'''
    #Parse --server_ip from command line
    parser = argparse.ArgumentParser(description='This program starts the TCP client with the option for the server IP to establish connection.')
    parser.add_argument('--server_ip', type=str, required=True)
    args = parser.parse_args()
    if len(args.server_ip) < 7 or len(args.server_ip) > 15 : #x.x.x.x - xxx.xxx.xxx.xxx
        parser.error("Enter a valid IP address for the server in format of x.x.x.x")
    return args.server_ip

def connect_to_server(server_ip, port):
    '''create socket and connect to server with error handling
       Returns (clientSocket, error_code) where error_code is 0 for success, 1 for gaierror, 2 for connection refused, 3 for other'''
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((server_ip, port))
        return clientSocket, 0
    except gaierror:  # ← Changed from socket.gaierror
        return None, 1
    except ConnectionRefusedError:
        return None, 2
    except Exception as e:
        return None, 3

def get_user_guess():
    '''takes in user guess and return as a string to go across the wire'''
    while True:
        try:
            guess = int(input("Enter your guess (1-100): "))
            if 1 <= guess <= 100:
                return str(guess)
            else:
                print("Guess must be between 1 and 100. Try again.")
        except ValueError:  #catches non int input
            print("Invalid input. Please enter a number.")

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

def main():
    server_ip = parse_args()
    clientSocket, error_code = connect_to_server(server_ip, PORT)
    
    #handle connection errors based on error code
    if error_code == 1:
        print(f"Error: Invalid server IP address '{server_ip}'")
        print("Please check the IP address and try again.")
        exit(1)
    elif error_code == 2:
        print(f"Error: Could not connect to server at {server_ip}:{PORT}")
        print("Make sure the server is running.")
        exit(1)
    elif error_code == 3:
        print(f"Error: Could not connect to server")
        exit(1)
    
    print("Welcome to Guess a Number! Guess quickly...or else you'll lose\n")
    
    try:
        guess = get_user_guess()
        clientSocket.sendall((guess + '\n').encode()) #add the newline so the server knows to clip it
        result = recv_line(clientSocket)
        if result:
            print(result)
    except Exception as e: 
        print(f"Error: {e}")
    finally:
        clientSocket.close()

if __name__ == "__main__":
    main()