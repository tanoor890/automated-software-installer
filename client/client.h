#ifndef CLIENT_H
#define CLIENT_H

#include "../common/protocol.h"

int  connect_to_server(const char *ip, int port);
int  request_list(int sockfd, char *list_buf, size_t buf_size);
int  request_download(int sockfd, int package_id, const char *save_dir,
                      char *out_filename, size_t fname_size,
                      progress_callback cb, void *user_data);
void disconnect(int sockfd);
int  parse_package_list(const char *list_data, Package *packages, int max_count);

#endif
