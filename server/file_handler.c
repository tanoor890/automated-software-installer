#include "file_handler.h"
#include "../common/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>

long get_file_size(const char *filepath) {
    struct stat st;
    if (stat(filepath, &st) != 0)
        return -1;
    return (long)st.st_size;
}

int send_file(int sockfd, const char *filepath, progress_callback cb, void *user_data) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        log_message("Cannot open file: %s", filepath);
        return -1;
    }

    long file_size = get_file_size(filepath);
    if (file_size < 0) {
        fclose(fp);
        return -1;
    }

    char buffer[BUFFER_SIZE];
    long total_sent = 0;
    size_t bytes_read;

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, fp)) > 0) {
        size_t offset = 0;
        while (offset < bytes_read) {
            ssize_t sent = send(sockfd, buffer + offset, bytes_read - offset, 0);
            if (sent <= 0) {
                log_message("Error sending file data");
                fclose(fp);
                return -1;
            }
            offset += sent;
            total_sent += sent;

            if (cb)
                cb(total_sent, file_size, user_data);
        }
    }

    fclose(fp);
    log_message("File sent successfully: %s (%ld bytes)", filepath, total_sent);
    return 0;
}
