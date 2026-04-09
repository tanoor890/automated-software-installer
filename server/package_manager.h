#ifndef PACKAGE_MANAGER_H
#define PACKAGE_MANAGER_H

#include "../common/protocol.h"

int  load_packages(const char *packages_file, Package *packages, int max_count);
int  list_packages(Package *packages, int count, char *buf, size_t buf_size);
Package *find_package(Package *packages, int count, int id);
int  reload_packages(const char *packages_file, Package *packages, int max_count);
int  add_package(const char *packages_file, const char *name, const char *filename, long size);

#endif
