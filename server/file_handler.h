#ifndef FILE_HANDLER_H
#define FILE_HANDLER_H

#include "../common/protocol.h"

int send_file(int sockfd, const char *filepath, progress_callback cb, void *user_data);
long get_file_size(const char *filepath);

#endif
