#include "package_manager.h"
#include "../common/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int load_packages(const char *packages_file, Package *packages, int max_count) {
    FILE *fp = fopen(packages_file, "r");
    if (!fp) {
        log_message("Cannot open packages file: %s", packages_file);
        return 0;
    }

    char line[MAX_LINE_LEN];
    int count = 0;

    while (fgets(line, sizeof(line), fp) && count < max_count) {
        trim_newline(line);
        if (strlen(line) == 0) continue;

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
    }

    fclose(fp);
    log_message("Loaded %d packages from %s", count, packages_file);
    return count;
}

int list_packages(Package *packages, int count, char *buf, size_t buf_size) {
    buf[0] = '\0';
    size_t offset = 0;

    for (int i = 0; i < count; i++) {
        char size_str[64];
        format_size(packages[i].size, size_str, sizeof(size_str));

        int written = snprintf(buf + offset, buf_size - offset,
                               "%d|%s|%s|%ld\n",
                               packages[i].id, packages[i].name,
                               packages[i].filename, packages[i].size);
        if (written < 0 || (size_t)written >= buf_size - offset)
            break;
        offset += written;
    }

    return count;
}

Package *find_package(Package *packages, int count, int id) {
    for (int i = 0; i < count; i++) {
        if (packages[i].id == id)
            return &packages[i];
    }
    return NULL;
}

int reload_packages(const char *packages_file, Package *packages, int max_count) {
    return load_packages(packages_file, packages, max_count);
}

int add_package(const char *packages_file, const char *name, const char *filename, long size) {
    Package packages[MAX_PACKAGES];
    int count = load_packages(packages_file, packages, MAX_PACKAGES);

    int new_id = 1;
    for (int i = 0; i < count; i++) {
        if (packages[i].id >= new_id)
            new_id = packages[i].id + 1;
    }

    FILE *fp = fopen(packages_file, "a");
    if (!fp) {
        log_message("Cannot open packages file for writing: %s", packages_file);
        return -1;
    }

    fprintf(fp, "%d|%s|%s|%ld\n", new_id, name, filename, size);
    fclose(fp);

    log_message("Added package: %d|%s|%s|%ld", new_id, name, filename, size);
    return new_id;
}
