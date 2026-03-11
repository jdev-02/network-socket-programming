#[author]
#CS3502 Computer Communications and Networks Programming Project Step 3
#Professor Xie

'''
-planning
-server:
-parse game_time from cmd line, bind to fixed port, generate the rand num(1,100), 
-accept client connection, then start game time countdown
-when game_time is up, send the echo message of what client put in and the rand num

-players = 0
-scorecard[] with all elements initialized to -1 and then if its not overwritten no guess was provided
-socket[]
while accepting new connections loop:  
    -assign player a player id
    -assign a socket to the given array or you can do dict with a key and socket as 
    -increment players and start timer once players =2
    
    -open a helper thread for the number of connections accepted (player)
        -pass player id and a socket (a way to communicate with the player) which is result from socket.accept returns a tuple of socket object
        -writes the players guess to the global guesses array
        -only compute a guess value is not -1
    -timer thread (when time expires, compare the values in the global array for given player and compare that to the generated value to see who wins and then send the results to the given players)
'''

from socket import *                             
from random import *
import argparse
import threading
import time 

HOST = ''                      #listen on all interfaces per instructions
PORT = 13000                                     
scorecard = []                 #scorecard array to track player guesses which will have default value of -1
sockets = []                   #global array for connection socket objects for each player
players = 0                    #counter for # of players
lock = threading.Lock()        #creates lock to protect shared resources
game_started = False           #our flag for timer to begin
shutdown_event = threading.Event()  #this allows us to stop the server cleanly so if keyboard event happens anywhere server can stop
guess_times = []               #parallel array to `scorecard` storing receive timestamps for tie-breaks


def parse_args():
    '''returns parsed value of game_time'''
    parser = argparse.ArgumentParser(description='This program starts the TCP server with options for game time and number of players')
    parser.add_argument('--game_time', type=int, required=True)
    parser.add_argument('--num_players', type=int, default=2, required=False)
    args = parser.parse_args()
    if args.game_time <= 0:
        parser.error("game_time option must be a postitive integer")
    if args.num_players <= 1:
        parser.error("num_players must be an integer >= 2")
    return args.game_time, args.num_players

def socket_setup(host, port):
    '''standard socket setup code for tcp'''
    serverSocket = socket(AF_INET, SOCK_STREAM)          #create a TCP socket (reliable, ordered byte stream)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #allow quick rebinding after a crash or restart of the server
    serverSocket.bind((host, port))                      #associate the socket with (ip, port) so clients can connect
    serverSocket.listen(2)                               #put into passive mode to accept incoming connections
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

def player_handler(player_id, connectionSocket, game_time):
    '''helper thread function to handle each player's connection and guess'''
    global scorecard #acces the scorecard array
    connectionSocket.settimeout(game_time)
    try:
        line = recv_line(connectionSocket)
        if line is not None:
            guess = int(line)
        else:
            guess = -1 #no guess bc closed connection without sending
    except ValueError:
        guess = -1 #treat invalid input as no guess
    except TimeoutError:
        guess = -1 #no guess received from client program
    
    lock.acquire()                               #acquire lock to safely write to shared scorecard
    scorecard[player_id] = guess                 #store this player's guess in the scorecard at their index
    #record the time the guess was received for tie-breaks; None if no valid guess
    if guess != -1:
        guess_times[player_id] = time.time()
    else:
        guess_times[player_id] = None
    lock.release()                               #release the lock after updating scorecard
    print(f"Player {player_id} submitted guess: {guess}")  #log the guess received

def outcome_timer(answer, game_time):
    """Timer thread function that waits for game time to expire, then determines winner and sends results"""
    global scorecard, sockets, guess_times #acees global arrays for updating state
    time.sleep(game_time) #sleep for length of the game, before we shoot out the outcome

    print(f"\nTime's up! Determining winner...") 
    
    #determine the winner by finding closest guess to answer
    winner_id = -1                               #initialize winner id (-1 means no winner)
    min_distance = float('inf')                  #initialize minimum distance to infinity for comparison default
    
    for player_id in range(len(scorecard)):      #iterate through all players in scorecard
        if scorecard[player_id] != -1:           #only consider players who submitted a guess
            distance = abs(scorecard[player_id] - answer)  #calculate distance from guess to answer
            if distance < min_distance:          #if this is closer than previous best
                min_distance = distance          #update minimum distance
                winner_id = player_id            #update winner id
            elif distance == min_distance:       #tie on distance -> use timestamp tie-break
                #both players have same closeness; pick the one who sent their guess earlier
                #guard against missing timestamps (None) - prefer whichever has a timestamp
                if guess_times[player_id] is not None and guess_times[winner_id] is not None:
                    if guess_times[player_id] < guess_times[winner_id]:
                        winner_id = player_id
                elif guess_times[player_id] is not None:
                    winner_id = player_id
    
    #send results to each player
    #identify all players who tied for the best (closest) distance
    tied_ids = [i for i in range(len(scorecard)) if scorecard[i] != -1 and abs(scorecard[i] - answer) == min_distance]

    for player_id in range(len(sockets)):        #iterate through all connected players
        conn = sockets[player_id]                #get the connection socket for this player
        guess = scorecard[player_id]             #get this player's guess from scorecard
        
        if guess == -1:                          #player did not submit a guess
            message = f"Time's up! You did not send a guess before the game time ran up. The answer was {answer}.\n"
        elif player_id == winner_id:             #this player won
            if guess == answer:                  #exact match case
                message = f"Congratulations! Your guess of {guess} exactly matches the answer of {answer}. You WIN!\n"
            else:                                #closest guess case (could be tie-break win)
                #if there was a tie on distance but this player won by being earlier, say so
                if len(tied_ids) > 1:
                    message = f"Congratulations! Your guess of {guess} was closest to the answer of {answer} and you were first among the tied closest guesses. You WIN!\n"
                else:
                    message = f"Congratulations! Your guess of {guess} was closest to the answer of {answer}. You WIN!\n"
        else:                                    #this player did not win
            if winner_id == -1:                  #no one submitted a guess
                message = f"No players submitted guesses. The answer was {answer}.\n"
            else:                                #someone else won
                #if this player tied on distance but lost on timestamp, notify they were too slow
                if player_id in tied_ids and len(tied_ids) > 1:
                    message = f"Sorry, your guess of {guess} was equally close but you were slower than Player {winner_id}. You LOSE. The answer was {answer}.\n"
                else:
                    message = f"Sorry, your guess of {guess} did not win. The answer was {answer}. Player {winner_id} won.\n"
        
        conn.sendall(message.encode())           #send the result message to this player
        conn.close()                             #close the connection to this player
    
    print("Game complete. All results sent.")    #log that game is finished


def main():
    global players, game_started, scorecard, sockets, guess_times  #access global variables for player management
    game_time, num_players = parse_args()        #parse command line arguments for game duration and required players
    serverSocket = socket_setup(HOST, PORT)      #set up the server socket
    serverSocket.settimeout(1.0)                 #make accept() periodically timeout so we can check shutdown_event
    #adjust backlog to support the configured number of players waiting to connect
    try:
        serverSocket.listen(num_players)
    except Exception:
        #if changing backlog fails, ignore — existing backlog will be used
        pass
    print(f"TCP server ready on {HOST}:{PORT}")
    print(f"Waiting for 2 or more players to connect...")
        
    try:
        while not shutdown_event.is_set():               #outer loop for multiple games checking for events to exit serversocket
            #new round
            players = 0
            scorecard = []
            sockets = []
            guess_times = []
            game_started = False
            answer = randint(1,100)
            
            print(f"New Game Started")
            print(f"Generated answer: {answer}")         #log the answer for debugging
            print(f"Waiting for 2 or more players to connect...")

            timer_thread = None                          #initialize timer thread variable
            try:
                while not shutdown_event.is_set():
                    try:
                        connectionSocket, clientAddress = serverSocket.accept()  #accept a new client connection (may timeout)
                    except timeout:
                        continue #no connection yet, loop back and recheck for shutdown event before
                    except OSError:
                        break #server socket closed -> exit inner loop
                    print(f"TCP connection from: {clientAddress}")
                    
                    lock.acquire()                       #acquire lock to safely modify shared variables
                    player_id = players                  #assign this player an id (0 or 1)
                    players += 1                         #increment the player count
                    scorecard.append(-1)                 #add a slot in scorecard for this player (initialized to -1)
                    guess_times.append(None)             #add a slot in guess_times for this player (initialized to None)
                    sockets.append(connectionSocket)     #add this socket to the sockets array

                    #if we've reached the required number of players, start the game timer
                    if players >= num_players and not game_started:  #check if we now have enough players and haven't started timer
                        game_started = True              #set flag to indicate game has started
                        print(f"\n2 players connected! Starting {game_time} second game timer...")
                        timer_thread = threading.Thread(target=outcome_timer, args=(answer, game_time))
                        timer_thread.start()             #start the outcome timer thread

                    lock.release()                       #release the lock after updating shared data
                    
                    #create and start a helper thread to handle this player's guess
                    t = threading.Thread(target=player_handler, args=(player_id, connectionSocket, game_time))
                    t.start()                            #start the player handler thread
                    
                    print(f"Player {player_id} connected. Total players: {players}")

                    if game_started: #break out of inner loop once timer is starting and games running
                        break

                #wait for the timer thread to complete before exiting this round
                if timer_thread is not None:             #if we created a timer thread
                    timer_thread.join()                  #wait for it to finish
            finally:
                #close down individual connections
                for conn in sockets:
                    try:
                        conn.close()
                    except:
                        pass

    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
        shutdown_event.set()

    finally:     
        try:
            serverSocket.close()
        except:
            pass
        print("Server socket exiting...") #now close down server socket after done closing individual sockets

if __name__ == "__main__":
    main()