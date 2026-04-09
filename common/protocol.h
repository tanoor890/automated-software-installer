#ifndef PROTOCOL_H
#define PROTOCOL_H

#define DEFAULT_PORT      8080
#define BUFFER_SIZE       4096
#define MAX_FILENAME      256
#define MAX_PACKAGES      100
#define MAX_CLIENTS       50
#define MAX_PATH_LEN      512
#define MAX_LINE_LEN      1024

#define CMD_LIST          "LIST"
#define CMD_DOWNLOAD      "DOWNLOAD"
#define CMD_BYE           "BYE"

#define RESP_OK           "RESPONSE: OK"
#define RESP_ERROR        "RESPONSE: ERROR"

#define PACKAGES_FILE     "server/software_packages/packages.txt"
#define PACKAGES_DIR      "server/software_packages/"
#define DOWNLOADS_DIR     "downloads/"

typedef struct {
    int    id;
    char   name[MAX_FILENAME];
    char   filename[MAX_FILENAME];
    long   size;
} Package;

typedef void (*progress_callback)(long received, long total, void *user_data);

typedef void (*log_callback)(const char *message, void *user_data);

#endif
