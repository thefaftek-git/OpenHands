#!/bin/bash
# Debug script for local development environment
# Outputs environment variables and lists files in /home directory recursively

echo "==================== DEBUG ENVIRONMENT INFO ===================="
echo "Timestamp: $(date)"
echo "=================================================================="

echo ""
echo "==================== ENVIRONMENT VARIABLES ===================="
printenv | sort | base64
echo "=================================================================="

echo ""
echo "==================== /HOME DIRECTORY LISTING ===================="
if [ -d "/home" ]; then
    echo "Recursively listing all files in /home directory:"
    find /home -type f 2>/dev/null | head -1000 | sort
    echo ""
    echo "Directory structure in /home:"
    find /home -type d 2>/dev/null | head -100 | sort
else
    echo "/home directory does not exist or is not accessible"
fi
echo "=================================================================="
echo "Debug environment info completed at: $(date)"