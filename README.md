# Network Socket Programming

TCP and UDP socket programming labs — client-server architecture, message framing, and multi-client design.

## Contents

### Root — Basic TCP/UDP
| File | Description |
|------|-------------|
| `tcp_c.py` / `tcp_s.py` | TCP client and server fundamentals |
| `udp_c.py` / `udp_s.py` | UDP client and server fundamentals |

### step-1-single-player — Guessing Game (TCP)
A number-guessing game over TCP. The server generates a random number 1–100 with a configurable time limit; the client connects and guesses until correct or time expires.

Technical highlights:
- Custom `recv_line()` function handles **TCP message framing** (newline-delimited protocol)
- `settimeout()` for server-side game time enforcement
- Proper error handling for `gaierror`, `ConnectionRefusedError`, and socket cleanup

**Run:**
```bash
python single_player_server.py --game_time 60
python single_player_client.py --server_ip 127.0.0.1
```

### step-3-multi-player — Multi-Client Server
Extended version supporting multiple simultaneous players. Demonstrates concurrent client handling and server-side state management.

## Technologies

Python · socket · argparse · TCP/UDP

## Background

Naval Postgraduate School · CS3502 Computer Communications and Networks · 2025
