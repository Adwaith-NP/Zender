# P2P File Sharing with Relay Server

A peer-to-peer file sharing application that enables direct file transfers between peers using a relay server for connection establishment.

## Overview

This project implements a peer-to-peer file sharing system where clients can connect to each other through a relay server. The relay server facilitates the initial connection between peers using Redis channels, after which peers can transfer files directly.


### Relay Server Setup

1. Navigate to the relay_server directory:
   ```
   cd relay_server
   ```
   
2 To install and run Redis:
   ```
   **MAC OS**
   brew install redis
   brew services start redis

   **Linux**
   sudo apt update
   sudo apt install redis-server
   sudo systemctl enable redis
   sudo systemctl start redis

   **Wondows**
   Install WSL.
   Open Ubuntu in WSL and run the same Linux steps above.
   ```

3 Start the relay server:
   ```
   python server.py runserver (if you want to run in a specific ip add python manage.py runserver <the ip>:<the port number>)
   ```

### install all packages

1. Install the required packages from the project root:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting a Client

To start a client, use the `zender.py` script with the relay server's IP address and port:

```
python zender.py <relay_server_ip>:<port>
```

Example:
```
python zender.py 122.32.44.55:8080
```

### Sharing Files

1. The sender initiates a file transfer by specifying the file path
2. The relay server connects the sender with available peers
3. Once connected, file transfer happens directly between peers the server only act as a relay 

## Features

- **Relay Server**: Uses Redis for managing connection channels between peers
- **Direct P2P Transfer**: After connection establishment, files transfer directly between peers the server act as relay 
- **Simple Command Line Interface**: Easy to use client interface
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **end - end encryption**: The data transaction is fully encrypted

## Dependencies


### Client and Relay Server
- See `requirements.txt` for dependencies

## License

[MIT License](LICENSE)

## Troubleshooting

### Common Issues

- **Connection Refused**: Make sure the relay server is running and the IP:Port is correct
- **Redis Connection Error**: Verify Redis is installed and running on the relay server
- **Permission Denied**: Ensure you have proper permissions to read/write files


<img width="846" alt="Screenshot 2025-05-08 at 9 03 29 PM" src="https://github.com/user-attachments/assets/00323825-7786-49ce-a810-601d73e3d3d7" />
