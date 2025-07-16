# Critical Debug Files (Sanitized)

This directory contains the critical debugging files requested, with all sensitive information redacted.

## Files Included:

- **runtime-logs/fw.jsonl** (401KB) - Main framework log file
- **runtime-logs/output.log** (66KB) - Output log file (sanitized)

These are the specific files mentioned as needed for debugging. Both files contain the complete logging output from the runtime execution.

## Security Notes:
- All GitHub tokens (ghu_, ghp_ patterns) have been redacted as [GITHUB_TOKEN_REDACTED]
- Secret hashes and long hex strings have been redacted as [SECRET_HASH_REDACTED] or [HASH_REDACTED]
- All functional debugging information is preserved while protecting sensitive data

## File Details:

```
runtime-logs/
├── fw.jsonl    (401KB) - Complete framework execution log
└── output.log  (66KB)  - Standard output capture (secrets redacted)
```

Total size: ~467KB of critical debugging data.