/*
 * Narrow launcher compatibility shim for sandboxes that permit
 * /proc/self/exe but deny /proc/<numeric-pid>/exe.  Lean 4.33.0 resolves its
 * own executable through the numeric form.  This shim changes only matching
 * readlink calls and is not part of any proof's trusted logic.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>

typedef ssize_t (*readlink_fn)(const char *, char *, size_t);

ssize_t readlink(const char *path, char *buffer, size_t size) {
    static readlink_fn real_readlink = NULL;
    if (real_readlink == NULL) {
        real_readlink = (readlink_fn)dlsym(RTLD_NEXT, "readlink");
    }
    if (path != NULL && strncmp(path, "/proc/", 6) == 0) {
        const char *suffix = strrchr(path, '/');
        if (suffix != NULL && strcmp(suffix, "/exe") == 0) {
            return real_readlink("/proc/self/exe", buffer, size);
        }
    }
    return real_readlink(path, buffer, size);
}
