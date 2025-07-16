# Encrypted Archive Files for Debugging

This directory contains encrypted archive files created for debugging purposes.

## Files:
- `critical_logs.tar.gz.gpg` - Critical log files from /home/runner/work/_temp including *.log and *.jsonl files
- `environment_vars.gz.gpg` - Complete environment variables (printenv output)
- `bash_config.tar.gz.gpg` - Bash configuration files (.profile, .bash*)
- `cache_sample.tar.gz.gpg` - Sample of cache files (small files only)

## Decryption:
All files are encrypted with ARCHIVE_PWD using AES256 cipher.

To decrypt:
```bash
gpg --batch --yes --decrypt --passphrase "$ARCHIVE_PWD" filename.tar.gz.gpg | tar -xzf -
```

For non-tar files:
```bash
gpg --batch --yes --decrypt --passphrase "$ARCHIVE_PWD" filename.gz.gpg | gunzip
```

## Note:
These archives contain selective data due to file size limitations. The complete archive script (create_archives.sh) can generate full archives if needed locally.
