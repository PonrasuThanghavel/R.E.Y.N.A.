# OpenClaw Integration Guide for Kimi-2.5-k2

## Overview

R.E.Y.N.A. has been successfully integrated with **OpenClaw** to use the **Kimi-2.5-k2** language model. This replaces the previous Moonshot AI HTTP API integration with a CLI-based approach.

## Architecture Change

### Before (HTTP API)
```
User Input → llm.py (HTTP requests) → Moonshot API → Response
```

### After (OpenClaw CLI)
```
User Input → llm.py (subprocess) → OpenClaw CLI → Kimi-2.5-k2 → Response → ActionSchema
```

## Setup Instructions

### 1. Install OpenClaw

```bash
# Install OpenClaw CLI
# Follow instructions at: https://github.com/openclaw/openclaw

# macOS (via Homebrew, if available)
brew install openclaw

# Linux / Manual Installation
# Download from: https://github.com/openclaw/openclaw/releases
# Add to PATH or install globally

# Verify installation
openclaw --version
```

### 2. Configure Kimi API Credentials

OpenClaw requires Kimi API credentials to be configured locally:

```bash
# Configure OpenClaw with your Kimi API key
openclaw configure --provider kimi --api-key YOUR_KIMI_API_KEY
```

Or set environment variables (if supported by your OpenClaw version):
```bash
export OPENCLAW_KIMI_API_KEY=your_api_key_here
```

### 3. Optional Configuration Verification

```bash
# Test OpenClaw connectivity
openclaw agent --agent main --json -m "test"
```

## Modified Files

### 1. **llm.py** 
- **Removed:** HTTP requests library calls, Moonshot API URL configuration
- **Added:** `subprocess` module for OpenClaw CLI invocation
- **Changes:**
  - `generate_action()` now uses `subprocess.run()` to call OpenClaw
  - JSON extraction handles OpenClaw response format
  - Comprehensive error handling for CLI failures
  - Model name set to `kimi-2.5-k2`
  - Agent name set to `main`

### 2. **.env.example**
- **Removed:** `MOONSHOT_API_KEY` placeholder
- **Added:** Comments about OpenClaw setup and PATH requirements

## Key Features

✅ **Kimi-2.5-k2 Model Support** - Uses the latest Kimi model through OpenClaw\
✅ **CLI-based Integration** - No HTTP API dependency\
✅ **JSON-Strict Output** - Ensures valid ActionSchema generation\
✅ **Error Handling** - Comprehensive error messages for debugging\
✅ **Timeout Protection** - 30-second timeout for safety\
✅ **Backward Compatible** - Maintains same ActionSchema interface

## Usage

Simply run R.E.Y.N.A. as before:

```bash
python main.py
```

The system will now use OpenClaw to process user inputs through kimi-2.5-k2.

## Troubleshooting

### "openclaw: command not found"
- Ensure OpenClaw is installed and in your PATH
- Try the full path: `/usr/local/bin/openclaw` (or wherever installed)
- Add OpenClaw directory to PATH: `export PATH=$PATH:/path/to/openclaw`

### "OpenClaw request timed out"
- Check network connectivity
- Verify Kimi API credentials are configured
- Try a simple test: `openclaw agent --agent main --json -m "hello"`

### "JSON decode error"
- Verify OpenClaw output format: `openclaw agent --help`
- Check that the `--json` flag is producing valid JSON output

### "Tool X is not registered"
- This is expected for user queries that don't match any tool
- The system will respond with `action: "unknown"`

## Reverting to HTTP API (if needed)

To revert to Moonshot AI HTTP API:

1. Restore original `llm.py` from version control
2. Add `requests>=2.30.0` back to requirements.txt if removed
3. Set `MOONSHOT_API_KEY` in `.env`
4. Update system prompt if needed

## Future Enhancements

- [ ] Support for multiple OpenClaw agents
- [ ] Streaming response handling
- [ ] Custom agent configuration
- [ ] Performance metrics/logging

## References

- [OpenClaw Documentation](https://github.com/openclaw/openclaw)
- [Kimi API Documentation](https://kimi.moonshot.cn/)
- [R.E.Y.N.A. Architecture](./readme.md)
