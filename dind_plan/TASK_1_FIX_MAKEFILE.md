# Task 1: Fix Makefile for dinD Support

## Goal
Fix the Makefile to properly support running OpenHands in docker-in-docker (dinD) mode.

## Issues Found
1. **Missing separator errors**: Multiple targets had missing separators between commands
2. **Duplicate start-frontend target**: The `start-frontend` target was defined multiple times with different recipes
3. **Incorrect indentation**: Some targets used spaces instead of tabs for command indentation

## Changes Made

### 1. Fixed docker-run target
- Corrected the `docker-run` target to use proper Makefile syntax with backslashes for line continuation
- Ensured all commands use tabs for indentation

### 2. Fixed run-dind target
- Added proper `run-dind` target that sets environment variables and starts both backend and frontend
- Created `_run_setup_dind` helper target for backend setup
- Created `start-frontend` target with proper WSL detection logic

### 3. Resolved duplicate targets
- Removed duplicate `start-frontend` definition to avoid conflicts

## Verification
The Makefile now builds successfully and can run the `make run-dind` command without syntax errors.

```bash
# Test the fix
cd /home/nathan/Repos/OpenHands/workspace/OpenHands
make run-dind
```

## Next Steps
1. Test the actual dinD functionality to ensure it works as expected
2. Add documentation for how to use the new `run-dind` target
3. Consider adding more environment variables for dinD configuration if needed
