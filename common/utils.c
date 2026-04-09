#include "utils.h"
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>

void format_size(long bytes, char *buf, size_t buf_size) {
    if (bytes >= 1073741824)
        snprintf(buf, buf_size, "%.2f GB", bytes / 1073741824.0);
    else if (bytes >= 1048576)
        snprintf(buf, buf_size, "%.2f MB", bytes / 1048576.0);
    else if (bytes >= 1024)
        snprintf(buf, buf_size, "%.2f KB", bytes / 1024.0);
    else
        snprintf(buf, buf_size, "%ld B", bytes);
}

void trim_newline(char *str) {
    if (!str) return;
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r'))
        str[--len] = '\0';
}

void get_timestamp(char *buf, size_t buf_size) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    strftime(buf, buf_size, "%Y-%m-%d %H:%M:%S", t);
}

void log_message(const char *format, ...) {
    char timestamp[64];
    get_timestamp(timestamp, sizeof(timestamp));
    fprintf(stdout, "[%s] ", timestamp);

    va_list args;
    va_start(args, format);
    vfprintf(stdout, format, args);
    va_end(args);

    fprintf(stdout, "\n");
    fflush(stdout);
}
