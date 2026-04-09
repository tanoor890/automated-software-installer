CC = gcc
CFLAGS = -Wall -Wextra -g
GTK_CFLAGS = $(shell pkg-config --cflags gtk+-3.0)
GTK_LIBS = $(shell pkg-config --libs gtk+-3.0)
PTHREAD = -lpthread

COMMON_SRC = common/utils.c

SERVER_SRC = server/server.c server/server_gui.c server/package_manager.c server/file_handler.c
CLIENT_SRC = client/client.c client/client_gui.c client/downloader.c client/installer.c

SERVER_BIN = server_app
CLIENT_BIN = client_app

.PHONY: all server client clean dirs

all: dirs server client
	@echo ""
	@echo "Build complete! Run with:"
	@echo "  ./server_app    (start the server)"
	@echo "  ./client_app    (start the client)"

dirs:
	@mkdir -p server/software_packages
	@mkdir -p downloads

server: dirs $(SERVER_SRC) $(COMMON_SRC)
	$(CC) $(CFLAGS) $(GTK_CFLAGS) -o $(SERVER_BIN) $(SERVER_SRC) $(COMMON_SRC) $(GTK_LIBS) $(PTHREAD)
	@echo "Server built: $(SERVER_BIN)"

client: dirs $(CLIENT_SRC) $(COMMON_SRC)
	$(CC) $(CFLAGS) $(GTK_CFLAGS) -o $(CLIENT_BIN) $(CLIENT_SRC) $(COMMON_SRC) $(GTK_LIBS) $(PTHREAD)
	@echo "Client built: $(CLIENT_BIN)"

clean:
	rm -f $(SERVER_BIN) $(CLIENT_BIN)
	@echo "Cleaned build artifacts"
