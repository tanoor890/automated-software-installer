#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <pthread.h>
#include <time.h>

#include "../common/protocol.h"
#include "../common/utils.h"
#include "package_manager.h"
#include "file_handler.h"

static int server_fd = -1;
static volatile int server_running = 0;
static Package packages[MAX_PACKAGES];
static int package_count = 0;
static pthread_mutex_t pkg_mutex = PTHREAD_MUTEX_INITIALIZER;

typedef struct {
    char ip[INET_ADDRSTRLEN];
    int  port;
    time_t connected_at;
} ClientInfo;

static ClientInfo connected_clients[MAX_CLIENTS];
static int client_count = 0;
static pthread_mutex_t client_mutex = PTHREAD_MUTEX_INITIALIZER;

static log_callback gui_log_cb = NULL;
static void *gui_log_data = NULL;

static void (*client_update_cb)(void) = NULL;

void server_set_log_callback(log_callback cb, void *data) {
    gui_log_cb = cb;
    gui_log_data = data;
}

void server_set_client_update_callback(void (*cb)(void)) {
    client_update_cb = cb;
}

static void server_log(const char *fmt, ...) {
    char message[MAX_LINE_LEN];
    va_list args;
    va_start(args, fmt);
    vsnprintf(message, sizeof(message), fmt, args);
    va_end(args);

    log_message("%s", message);

    if (gui_log_cb)
        gui_log_cb(message, gui_log_data);
}

int get_client_count(void) {
    pthread_mutex_lock(&client_mutex);
    int count = client_count;
    pthread_mutex_unlock(&client_mutex);
    return count;
}

void get_connected_clients_copy(ClientInfo *out, int *count) {
    pthread_mutex_lock(&client_mutex);
    *count = client_count;
    if (out && client_count > 0)
        memcpy(out, connected_clients, sizeof(ClientInfo) * client_count);
    pthread_mutex_unlock(&client_mutex);
}

static void add_client(const char *ip, int port) {
    pthread_mutex_lock(&client_mutex);
    if (client_count < MAX_CLIENTS) {
        strncpy(connected_clients[client_count].ip, ip, INET_ADDRSTRLEN - 1);
        connected_clients[client_count].port = port;
        connected_clients[client_count].connected_at = time(NULL);
        client_count++;
    }
    pthread_mutex_unlock(&client_mutex);
    if (client_update_cb) client_update_cb();
}

static void remove_client(const char *ip, int port) {
    pthread_mutex_lock(&client_mutex);
    for (int i = 0; i < client_count; i++) {
        if (strcmp(connected_clients[i].ip, ip) == 0 &&
            connected_clients[i].port == port) {
            for (int j = i; j < client_count - 1; j++)
                connected_clients[j] = connected_clients[j + 1];
            client_count--;
            break;
        }
    }
    pthread_mutex_unlock(&client_mutex);
    if (client_update_cb) client_update_cb();
}

static void handle_client(int client_fd, const char *client_ip, int client_port) {
    char buffer[BUFFER_SIZE];
    server_log("Client connected: %s:%d", client_ip, client_port);
    add_client(client_ip, client_port);

    while (server_running) {
        memset(buffer, 0, sizeof(buffer));
        ssize_t n = recv(client_fd, buffer, sizeof(buffer) - 1, 0);
        if (n <= 0) {
            server_log("Client disconnected: %s:%d", client_ip, client_port);
            break;
        }

        trim_newline(buffer);
        server_log("Received from %s:%d -> %s", client_ip, client_port, buffer);

        if (strcmp(buffer, CMD_LIST) == 0) {
            char list_buf[BUFFER_SIZE * 8];
            pthread_mutex_lock(&pkg_mutex);
            list_packages(packages, package_count, list_buf, sizeof(list_buf));
            pthread_mutex_unlock(&pkg_mutex);

            char response[BUFFER_SIZE * 8];
            snprintf(response, sizeof(response), "%s\n%s", RESP_OK, list_buf);
            send(client_fd, response, strlen(response), 0);
            server_log("Sent package list to %s:%d (%d packages)", client_ip, client_port, package_count);

        } else if (strncmp(buffer, CMD_DOWNLOAD, strlen(CMD_DOWNLOAD)) == 0) {
            int pkg_id = atoi(buffer + strlen(CMD_DOWNLOAD) + 1);

            pthread_mutex_lock(&pkg_mutex);
            Package *pkg = find_package(packages, package_count, pkg_id);
            pthread_mutex_unlock(&pkg_mutex);

            if (pkg) {
                char filepath[MAX_PATH_LEN];
                snprintf(filepath, sizeof(filepath), "%s%s", PACKAGES_DIR, pkg->filename);

                long fsize = get_file_size(filepath);
                if (fsize < 0) {
                    char err[BUFFER_SIZE];
                    snprintf(err, sizeof(err), "%s File not found on disk", RESP_ERROR);
                    send(client_fd, err, strlen(err), 0);
                    server_log("File not found: %s", filepath);
                } else {
                    char ok[BUFFER_SIZE];
                    snprintf(ok, sizeof(ok), "%s %ld %s", RESP_OK, fsize, pkg->filename);
                    send(client_fd, ok, strlen(ok), 0);

                    char ack[16];
                    memset(ack, 0, sizeof(ack));
                    recv(client_fd, ack, sizeof(ack) - 1, 0);

                    server_log("Sending file: %s (%ld bytes) to %s:%d", pkg->filename, fsize, client_ip, client_port);
                    if (send_file(client_fd, filepath, NULL, NULL) == 0) {
                        server_log("File sent successfully: %s to %s:%d", pkg->filename, client_ip, client_port);
                    } else {
                        server_log("Failed to send file: %s to %s:%d", pkg->filename, client_ip, client_port);
                    }
                }
            } else {
                char err[BUFFER_SIZE];
                snprintf(err, sizeof(err), "%s Package ID %d not found", RESP_ERROR, pkg_id);
                send(client_fd, err, strlen(err), 0);
                server_log("Package not found: ID %d", pkg_id);
            }

        } else if (strcmp(buffer, CMD_BYE) == 0) {
            server_log("Client %s:%d sent BYE", client_ip, client_port);
            break;

        } else {
            char err[BUFFER_SIZE];
            snprintf(err, sizeof(err), "%s Unknown command", RESP_ERROR);
            send(client_fd, err, strlen(err), 0);
        }
    }

    remove_client(client_ip, client_port);
    close(client_fd);
}

typedef struct {
    int  client_fd;
    char client_ip[INET_ADDRSTRLEN];
    int  client_port;
} ClientThreadArgs;

static void *client_thread_func(void *arg) {
    ClientThreadArgs *cta = (ClientThreadArgs *)arg;
    handle_client(cta->client_fd, cta->client_ip, cta->client_port);
    free(cta);
    return NULL;
}

int setup_server(int port) {
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        server_log("Failed to create socket");
        return -1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        server_log("Failed to bind to port %d", port);
        close(server_fd);
        server_fd = -1;
        return -1;
    }

    if (listen(server_fd, MAX_CLIENTS) < 0) {
        server_log("Failed to listen");
        close(server_fd);
        server_fd = -1;
        return -1;
    }

    server_log("Server listening on port %d", port);
    return 0;
}

void server_reload_packages(void) {
    pthread_mutex_lock(&pkg_mutex);
    package_count = reload_packages(PACKAGES_FILE, packages, MAX_PACKAGES);
    pthread_mutex_unlock(&pkg_mutex);
    server_log("Reloaded packages: %d available", package_count);
}

void *server_accept_loop(void *arg) {
    (void)arg;

    pthread_mutex_lock(&pkg_mutex);
    package_count = load_packages(PACKAGES_FILE, packages, MAX_PACKAGES);
    pthread_mutex_unlock(&pkg_mutex);

    server_running = 1;

    while (server_running) {
        struct sockaddr_in client_addr;
        socklen_t addr_len = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &addr_len);

        if (client_fd < 0) {
            if (server_running)
                server_log("Accept failed");
            continue;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        int client_port = ntohs(client_addr.sin_port);

        ClientThreadArgs *cta = malloc(sizeof(ClientThreadArgs));
        if (!cta) {
            server_log("Memory allocation failed for client thread");
            close(client_fd);
            continue;
        }

        cta->client_fd = client_fd;
        strncpy(cta->client_ip, client_ip, INET_ADDRSTRLEN - 1);
        cta->client_ip[INET_ADDRSTRLEN - 1] = '\0';
        cta->client_port = client_port;

        pthread_t tid;
        if (pthread_create(&tid, NULL, client_thread_func, cta) != 0) {
            server_log("Failed to create client thread");
            close(client_fd);
            free(cta);
        } else {
            pthread_detach(tid);
        }
    }

    return NULL;
}

int start_server(int port) {
    if (server_running) {
        server_log("Server is already running");
        return -1;
    }

    if (setup_server(port) < 0)
        return -1;

    pthread_t thread;
    if (pthread_create(&thread, NULL, server_accept_loop, NULL) != 0) {
        server_log("Failed to create server thread");
        close(server_fd);
        return -1;
    }
    pthread_detach(thread);

    return 0;
}

void stop_server(void) {
    if (!server_running) {
        server_log("Server is not running");
        return;
    }

    server_running = 0;

    if (server_fd >= 0) {
        shutdown(server_fd, SHUT_RDWR);
        close(server_fd);
        server_fd = -1;
    }

    server_log("Server stopped");
}

int is_server_running(void) {
    return server_running;
}

int get_package_count(void) {
    pthread_mutex_lock(&pkg_mutex);
    int count = package_count;
    pthread_mutex_unlock(&pkg_mutex);
    return count;
}

Package *get_packages(int *count) {
    pthread_mutex_lock(&pkg_mutex);
    *count = package_count;
    pthread_mutex_unlock(&pkg_mutex);
    return packages;
}
