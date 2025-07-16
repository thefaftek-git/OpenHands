#!/bin/bash
# Debug script for local development environment
# Outputs environment variables and comprehensive directory listings
# Saves output to debug_output.txt file

OUTPUT_FILE="debug_output.txt"
ENV_OUTPUT_FILE="environment_base64.txt"

# Save base64-encoded environment variables to separate file
echo "Saving base64-encoded environment variables to: $ENV_OUTPUT_FILE"
printenv | sort | base64 > "$ENV_OUTPUT_FILE"

{
echo "==================== DEBUG ENVIRONMENT INFO ===================="
echo "Timestamp: $(date)"
echo "=================================================================="

echo ""
echo "==================== ENVIRONMENT VARIABLES ===================="
printenv | sort | base64
echo "=================================================================="

echo ""
echo "==================== /HOME DIRECTORY ANALYSIS ===================="
if [ -d "/home" ]; then
    echo "Direct folders under /home (including hidden ones):"
    if command -v sudo >/dev/null 2>&1; then
        sudo ls -la /home 2>/dev/null || ls -la /home 2>/dev/null
    else
        ls -la /home 2>/dev/null
    fi
    echo ""
    echo "All directories in /home recursively (with sudo if available):"
    if command -v sudo >/dev/null 2>&1; then
        sudo find /home -type d 2>/dev/null | head -500 | sort
    else
        find /home -type d 2>/dev/null | head -500 | sort
    fi
    echo ""
    echo "All files in /home recursively (limited to first 1000):"
    if command -v sudo >/dev/null 2>&1; then
        sudo find /home -type f 2>/dev/null | head -1000 | sort
    else
        find /home -type f 2>/dev/null | head -1000 | sort
    fi
else
    echo "/home directory does not exist or is not accessible"
fi
echo "=================================================================="

echo ""
echo "==================== ROOT DIRECTORY ANALYSIS ===================="
echo "Listing directories from root (/) - excluding problematic paths:"
if command -v sudo >/dev/null 2>&1; then
    sudo find / -maxdepth 1 -type d 2>/dev/null | sort
    echo ""
    echo "Recursive directory listing from root (limited to first 2000, excluding /proc, /sys, /dev):"
    sudo find / -type d \( -path '/proc' -o -path '/sys' -o -path '/dev' \) -prune -o -type d -print 2>/dev/null | head -2000 | sort
    echo ""
    echo "Recursive file listing from root (limited to first 5000, excluding /proc, /sys, /dev):"
    sudo find / -type f \( -path '/proc' -o -path '/sys' -o -path '/dev' \) -prune -o -type f -print 2>/dev/null | head -5000 | sort
else
    find / -maxdepth 1 -type d 2>/dev/null | sort
    echo ""
    echo "Recursive directory listing from root (limited, no sudo available):"
    find / -type d \( -path '/proc' -o -path '/sys' -o -path '/dev' \) -prune -o -type d -print 2>/dev/null | head -2000 | sort
    echo ""
    echo "Recursive file listing from root (limited, no sudo available):"
    find / -type f \( -path '/proc' -o -path '/sys' -o -path '/dev' \) -prune -o -type f -print 2>/dev/null | head -5000 | sort
fi
echo "=================================================================="
echo "Debug environment info completed at: $(date)"
} > "$OUTPUT_FILE"

echo "Debug environment info saved to: $OUTPUT_FILE"
echo "Base64-encoded environment variables saved to: $ENV_OUTPUT_FILE"