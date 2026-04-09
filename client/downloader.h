#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#include "../common/protocol.h"

int receive_file(int sockfd, const char *save_path, long file_size,
                 progress_callback cb, void *user_data);

#endif
