# Automated Software Installation Server

> **CSE 324 — Operating Systems Lab Project**

A client-server system written in C that allows a server to host software packages and clients to browse, download, and automatically install them over TCP sockets. Both server and client feature GTK 3 graphical user interfaces.

## Team

| Role | Name | ID |
|---|---|---|
| Project Leader & System Architect | Md. Al Shahariar Shuvo | 232-15-097 |
| Server-Side Developer | Abdullah Al Maruf | 232-15-180 |
| Client-Side Developer | Sibgatullah Mahi | 232-15-015 |
| Network & Socket Programmer | Reyaid Bin Alam Utsho | 232-15-508 |
| Testing & Documentation Engineer | Ikramul Hasan Jowel | 232-15-819 |

## Architecture

```
Server (Linux)                         Client (Linux)
┌─────────────────┐                    ┌─────────────────┐
│  Server GUI     │                    │  Client GUI     │
│  (GTK 3)        │                    │  (GTK 3)        │
│  ┌────────────┐ │    TCP Socket      │  ┌────────────┐ │
│  │ server.c   │◄├────────────────────┤► │ client.c   │ │
│  └────────────┘ │  1. Package list   │  └────────────┘ │
│  ┌────────────┐ │  2. File transfer  │  ┌────────────┐ │
│  │ packages/  │ │                    │  │ downloads/ │ │
│  └────────────┘ │                    │  └────────────┘ │
└─────────────────┘                    │  ┌────────────┐ │
                                       │  │ installer  │ │
                                       │  └────────────┘ │
                                       └─────────────────┘
```

## Project Structure

```
utsho_project/
├── server/
│   ├── server.c               # Server logic (socket, pthreads, command loop)
│   ├── server_gui.c           # GTK 3 GUI for server management
│   ├── file_handler.c/.h      # Chunked file sending over socket
│   ├── package_manager.c/.h   # Package metadata management
│   └── software_packages/     # Installer files + packages.txt
├── client/
│   ├── client.c/.h            # Client networking (connect, list, download)
│   ├── client_gui.c           # GTK 3 GUI for client application
│   ├── downloader.c/.h        # Chunked file receiving
│   └── installer.c/.h         # Auto-install (.deb, .sh, .AppImage, .tar.gz)
├── common/
│   ├── protocol.h             # Shared constants and types
│   └── utils.c/.h             # Shared utilities
├── Makefile                   # Build system
└── README.md
```

## Dependencies

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install build-essential libgtk-3-dev pkg-config
```

### Fedora / RHEL

```bash
sudo dnf install gcc make gtk3-devel pkgconfig
```

## Building

```bash
# Build both server and client
make all

# Build only the server
make server

# Build only the client
make client

# Clean build artifacts
make clean
```

## Running

### Step 1: Start the Server

```bash
./server_app
```

1. Set the listening port (default: 8080)
2. Click **Start Server**
3. The package list loads automatically from `server/software_packages/packages.txt`
4. The server log shows all activity in real-time

### Step 2: Start the Client (in a new terminal)

```bash
./client_app
```

1. Enter the server IP address (use `127.0.0.1` for localhost testing)
2. Enter the port number (default: 8080)
3. Click **Connect**
4. Click **Refresh List** to see available packages
5. Select a package from the list
6. Click **Download & Install**
7. Watch the progress bar fill in real-time
8. After download, a dialog asks whether to auto-install
9. Click **Yes** to run the installer automatically

## OS Concepts Demonstrated

| Concept | Where Used |
|---|---|
| **Socket Programming** | TCP server/client communication using POSIX sockets (`socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`) |
| **Concurrent Client Handling** | Each client is handled in a separate POSIX thread (`pthread_create()`) |
| **Thread Synchronization** | Mutexes (`pthread_mutex_t`) protect shared data (package list, client list) |
| **Process Execution** | Auto-installer uses `system()` to execute downloaded packages |
| **File I/O** | Chunked binary file transfer with `fread()`/`fwrite()` |
| **Network Protocol Design** | Custom text-based command protocol (LIST, DOWNLOAD, BYE) |
| **GUI Event Loop** | GTK main loop with `g_idle_add()` for thread-safe GUI updates |

## Package Metadata Format

The file `server/software_packages/packages.txt` uses pipe-delimited format:

```
ID|Display Name|Filename|Size in bytes
```

Example:
```
1|Hello World Installer|hello-world.sh|685
2|System Information Tool|system-info.sh|1263
3|Disk Cleaner Utility|disk-cleaner.sh|810
```

## Communication Protocol

| Command | Direction | Description |
|---|---|---|
| `LIST` | Client → Server | Request list of available packages |
| `DOWNLOAD <id>` | Client → Server | Request download of a specific package |
| `RESPONSE: OK <data>` | Server → Client | Success response with data |
| `RESPONSE: ERROR <msg>` | Server → Client | Error response |
| `BYE` | Client → Server | Disconnect |

File transfers use raw binary `send()`/`recv()` in 4096-byte chunks with a size header.

## Auto-Installation

The client auto-detects file types and runs the appropriate installation command:

| File Type | Command |
|---|---|
| `.deb` | `sudo dpkg -i <file>` |
| `.rpm` | `sudo rpm -i <file>` |
| `.sh` | `chmod +x <file> && ./<file>` |
| `.AppImage` | `chmod +x <file> && ./<file>` |
| `.tar.gz` | `tar -xzf <file>` |

## Testing

1. Run server and client on the same machine using `127.0.0.1`
2. Start the server, click Start Server
3. Start the client, connect to `127.0.0.1:8080`
4. Refresh package list, download a package, confirm auto-install
5. Open multiple client windows to test concurrent connections
6. Check server GUI for real-time client tracking and activity logs

## Platform

This project targets **Linux** exclusively and uses:
- POSIX sockets (`sys/socket.h`, `arpa/inet.h`)
- POSIX threads (`pthread.h`) for concurrent client handling and GUI background tasks
- Mutexes for thread-safe shared data access
- GTK 3 for graphical interfaces
- `system()` for auto-installation of downloaded packages
