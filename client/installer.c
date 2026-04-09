#include "installer.h"
#include "../common/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *get_extension(const char *filename) {
    const char *dot = strrchr(filename, '.');
    return dot ? dot : "";
}

const char *get_install_command(const char *filepath) {
    const char *ext = get_extension(filepath);

    if (strcmp(ext, ".deb") == 0)
        return "sudo dpkg -i";
    else if (strcmp(ext, ".rpm") == 0)
        return "sudo rpm -i";
    else if (strcmp(ext, ".sh") == 0)
        return "chmod +x %s && ./%s";
    else if (strcmp(ext, ".AppImage") == 0)
        return "chmod +x";
    else if (strcmp(ext, ".gz") == 0 || strcmp(ext, ".tgz") == 0)
        return "tar -xzf";
    else if (strcmp(ext, ".bz2") == 0)
        return "tar -xjf";
    else if (strcmp(ext, ".xz") == 0)
        return "tar -xJf";

    return NULL;
}

int auto_install(const char *filepath) {
    if (!filepath) return -1;

    const char *ext = get_extension(filepath);
    char command[1024];

    log_message("Auto-installing: %s", filepath);

    if (strcmp(ext, ".deb") == 0) {
        snprintf(command, sizeof(command), "sudo dpkg -i \"%s\" 2>&1", filepath);
    } else if (strcmp(ext, ".rpm") == 0) {
        snprintf(command, sizeof(command), "sudo rpm -i \"%s\" 2>&1", filepath);
    } else if (strcmp(ext, ".sh") == 0) {
        snprintf(command, sizeof(command),
                 "chmod +x \"%s\" && \"%s\" 2>&1", filepath, filepath);
    } else if (strcmp(ext, ".AppImage") == 0) {
        snprintf(command, sizeof(command),
                 "chmod +x \"%s\" && \"%s\" 2>&1", filepath, filepath);
    } else if (strcmp(ext, ".gz") == 0 || strcmp(ext, ".tgz") == 0) {
        snprintf(command, sizeof(command),
                 "tar -xzf \"%s\" -C \"%s\" 2>&1", filepath, "downloads/");
    } else if (strcmp(ext, ".bz2") == 0) {
        snprintf(command, sizeof(command),
                 "tar -xjf \"%s\" -C \"%s\" 2>&1", filepath, "downloads/");
    } else if (strcmp(ext, ".xz") == 0) {
        snprintf(command, sizeof(command),
                 "tar -xJf \"%s\" -C \"%s\" 2>&1", filepath, "downloads/");
    } else {
        log_message("Unknown file type: %s — cannot auto-install", ext);
        return -1;
    }

    log_message("Running: %s", command);
    int ret = system(command);

    if (ret == 0) {
        log_message("Installation completed successfully: %s", filepath);
    } else {
        log_message("Installation failed with exit code %d: %s", ret, filepath);
    }

    return ret;
}
