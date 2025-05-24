#!/bin/bash

# Get Ollama URL from environment or use default
OLLAMA_URL=${OLLAMA_URL:-"http://localhost:11434"}

# Parse command line arguments
MCP_CONFIG=""
WINDOW_SIZE=""

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mcp-config)
      MCP_CONFIG="$2"
      shift 2
      ;;
    --window-size)
      WINDOW_SIZE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--mcp-config <config_file>] [--window-size <size>]"
      exit 1
      ;;
  esac
done

# Check if Ollama is running
if ! curl -s $OLLAMA_URL/api/version > /dev/null; then
    echo "Error: Ollama server is not running at $OLLAMA_URL"
    echo "Please start Ollama before running this script"
    exit 1
fi

# Check if any models are available
if ! ollama list > /dev/null 2>&1; then
    echo "Warning: No Ollama models found or ollama command not available"
    echo "You may need to run: ollama pull llama3"
    echo "Continuing anyway..."
fi

# Activate virtual environment
source venv/bin/activate

# Export Ollama URL for the agent to use
export OLLAMA_URL

# Add src directory to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Build command with arguments
CMD="python -m src.app.agent"
if [ -n "$MCP_CONFIG" ]; then
    CMD="$CMD --mcp-config $MCP_CONFIG"
fi
if [ -n "$WINDOW_SIZE" ]; then
    CMD="$CMD --window-size $WINDOW_SIZE"
fi

# Run the application
echo "Running: $CMD"
$CMD

# Deactivate virtual environment when done
deactivate
