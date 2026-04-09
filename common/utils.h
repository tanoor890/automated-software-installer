#ifndef UTILS_H
#define UTILS_H

#include <stddef.h>

void format_size(long bytes, char *buf, size_t buf_size);
void trim_newline(char *str);
void get_timestamp(char *buf, size_t buf_size);
void log_message(const char *format, ...);

#endif
