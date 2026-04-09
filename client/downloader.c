#include "downloader.h"
#include "../common/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <errno.h>

static int ensure_directory(const char *dir) {
    struct stat st;
    if (stat(dir, &st) == -1) {
        if (mkdir(dir, 0755) == -1 && errno != EEXIST) {
            log_message("Failed to create directory: %s", dir);
            return -1;
        }
    }
    return 0;
}

int receive_file(int sockfd, const char *save_path, long file_size,
                 progress_callback cb, void *user_data) {

    /* Ensure downloads directory exists */
    ensure_directory(DOWNLOADS_DIR);

    FILE *fp = fopen(save_path, "wb");
    if (!fp) {
        log_message("Cannot create file: %s", save_path);
        return -1;
    }

    char buffer[BUFFER_SIZE];
    long total_received = 0;

    while (total_received < file_size) {
        long remaining = file_size - total_received;
        size_t to_read = remaining < BUFFER_SIZE ? remaining : BUFFER_SIZE;

        ssize_t n = recv(sockfd, buffer, to_read, 0);
        if (n <= 0) {
            log_message("Connection lost during file transfer at %ld/%ld bytes",
                        total_received, file_size);
            fclose(fp);
            return -1;
        }

        fwrite(buffer, 1, n, fp);
        total_received += n;

        if (cb)
            cb(total_received, file_size, user_data);
    }

    fclose(fp);
    log_message("File received: %s (%ld bytes)", save_path, total_received);
    return 0;
}
