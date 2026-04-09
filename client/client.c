#include "client.h"
#include "downloader.h"
#include "../common/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

int connect_to_server(const char *ip, int port) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        log_message("Failed to create socket");
        return -1;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        log_message("Invalid server address: %s", ip);
        close(sockfd);
        return -1;
    }

    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        log_message("Connection to %s:%d failed", ip, port);
        close(sockfd);
        return -1;
    }

    log_message("Connected to server %s:%d", ip, port);
    return sockfd;
}

int request_list(int sockfd, char *list_buf, size_t buf_size) {
    if (send(sockfd, CMD_LIST "\n", strlen(CMD_LIST) + 1, 0) < 0) {
        log_message("Failed to send LIST command");
        return -1;
    }

    memset(list_buf, 0, buf_size);
    ssize_t n = recv(sockfd, list_buf, buf_size - 1, 0);
    if (n <= 0) {
        log_message("Failed to receive package list");
        return -1;
    }

    /* Check for OK response */
    if (strncmp(list_buf, RESP_OK, strlen(RESP_OK)) != 0) {
        log_message("Server error: %s", list_buf);
        return -1;
    }

    /* Skip past "RESPONSE: OK\n" */
    char *data = strchr(list_buf, '\n');
    if (data) {
        memmove(list_buf, data + 1, strlen(data + 1) + 1);
    }

    return 0;
}

int parse_package_list(const char *list_data, Package *packages, int max_count) {
    int count = 0;
    char data_copy[BUFFER_SIZE * 4];
    strncpy(data_copy, list_data, sizeof(data_copy) - 1);
    data_copy[sizeof(data_copy) - 1] = '\0';

    char *line = strtok(data_copy, "\n");
    while (line && count < max_count) {
        int id;
        char name[MAX_FILENAME], filename[MAX_FILENAME];
        long size;

        if (sscanf(line, "%d|%[^|]|%[^|]|%ld", &id, name, filename, &size) == 4) {
            packages[count].id = id;
            strncpy(packages[count].name, name, MAX_FILENAME - 1);
            strncpy(packages[count].filename, filename, MAX_FILENAME - 1);
            packages[count].size = size;
            count++;
        }
        line = strtok(NULL, "\n");
    }

    return count;
}

int request_download(int sockfd, int package_id, const char *save_dir,
                     char *out_filename, size_t fname_size,
                     progress_callback cb, void *user_data) {

    char cmd[BUFFER_SIZE];
    snprintf(cmd, sizeof(cmd), "%s %d\n", CMD_DOWNLOAD, package_id);

    if (send(sockfd, cmd, strlen(cmd), 0) < 0) {
        log_message("Failed to send DOWNLOAD command");
        return -1;
    }

    char response[BUFFER_SIZE];
    memset(response, 0, sizeof(response));
    ssize_t n = recv(sockfd, response, sizeof(response) - 1, 0);
    if (n <= 0) {
        log_message("Failed to receive download response");
        return -1;
    }

    if (strncmp(response, RESP_ERROR, strlen(RESP_ERROR)) == 0) {
        log_message("Server error: %s", response);
        return -1;
    }

    /* Parse "RESPONSE: OK <size> <filename>" */
    long file_size = 0;
    char filename[MAX_FILENAME] = {0};

    if (sscanf(response, "RESPONSE: OK %ld %s", &file_size, filename) != 2) {
        log_message("Invalid server response: %s", response);
        return -1;
    }

    if (out_filename && fname_size > 0)
        strncpy(out_filename, filename, fname_size - 1);

    /* Send acknowledgment to server */
    send(sockfd, "READY\n", 6, 0);

    char save_path[MAX_PATH_LEN];
    snprintf(save_path, sizeof(save_path), "%s%s", save_dir, filename);

    log_message("Downloading: %s (%ld bytes)", filename, file_size);

    if (receive_file(sockfd, save_path, file_size, cb, user_data) != 0) {
        log_message("Download failed: %s", filename);
        return -1;
    }

    log_message("Download complete: %s", save_path);
    return 0;
}

void disconnect(int sockfd) {
    if (sockfd >= 0) {
        send(sockfd, CMD_BYE "\n", strlen(CMD_BYE) + 1, 0);
        close(sockfd);
        log_message("Disconnected from server");
    }
}
