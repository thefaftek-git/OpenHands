# Phase 1: Foundation and Configuration

## Task 1.1: Add dinD Mode Configuration Option

### Description
Add configuration options to enable/disable dinD mode in the SandboxConfig.

### Files to Modify
- `openhands/core/config/sandbox_config.py`
- `openhands/core/config/openhands_config.py`

### Implementation Steps

1. **Add new fields to SandboxConfig**:
   - `enable_dind: bool = Field(default=False)` - Enable dinD mode
   - `dind_base_image: str | None = Field(default=None)` - Base image for dinD container
   - `dind_volumes: str | None = Field(default=None)` - Additional volumes for dinD

2. **Update OpenHandsConfig** to include the new SandboxConfig fields.

### Estimated Time: 30 minutes

---

## Task 1.2: Update Runtime Selection Logic

### Description
Modify runtime selection logic to support dinD mode as a first-class citizen.

### Files to Modify
- `openhands/runtime/__init__.py`
- `openhands/runtime/impl/docker/`

### Implementation Steps

1. **Add dinD runtime option** in `_DEFAULT_RUNTIME_CLASSES`:
   ```python
   _DEFAULT_RUNTIME_CLASSES['dind'] = DockerRuntime  # or create DinDRuntime if needed
   ```

2. **Update get_runtime_cls()** function to handle dinD selection.

3. **Create DinDRuntime class** (if needed) that extends DockerRuntime with dinD-specific optimizations.

### Estimated Time: 30 minutes

---

## Task 1.3: Update Makefile for dinD Support

### Description
Add make targets to support dinD development mode.

### Files to Modify
- `Makefile`

### Implementation Steps

1. **Add new make targets**:
   - `make dind-dev`: Start development in dinD mode
   - `make run-dind`: Run OpenHands in dinD mode
   - `make build-dind`: Build for dinD environment

2. **Update existing targets** to support dinD flag:
   ```bash
   make run RUNTIME=dind
   ```

### Estimated Time: 30 minutes

---

## Task 1.4: Add Environment Variable Support

### Description
Add environment variables to control dinD behavior.

### Files to Modify
- `openhands/core/config/openhands_config.py`

### Implementation Steps

1. **Add support for environment variables**:
   - `OPENHANDS_RUNTIME=dind` - Force use of dinD runtime
   - `OPENHANDS_DIND_ENABLE=true/false` - Enable/disable dinD mode

2. **Update config loading logic** to respect these environment variables.

### Estimated Time: 30 minutes

---

## Task 1.5: Update Configuration Documentation

### Description
Document the new configuration options for dinD support.

### Files to Create/Modify
- `docs/configuration/dind.md` (new file)
- Update existing documentation files

### Implementation Steps

1. **Create comprehensive documentation** explaining:
   - How to enable dinD mode
   - Available configuration options
   - Environment variables
   - Examples and best practices

2. **Update README.md** with dinD section.

### Estimated Time: 30 minutes

---

## Phase 1 Summary
Phase 1 focuses on laying the foundation for dinD support by adding configuration options, updating runtime selection logic, and integrating with the build system. This phase ensures that dinD can be easily enabled and configured without breaking existing workflows.

**Total Estimated Time: ~2 hours**
