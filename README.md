# Strands Agent Demo with Ollama and MCP Integration

A simple interactive demonstration project for working with the strands library, Ollama, and MCP clients, featuring model selection and configurable server URLs.

## Prerequisites

1. Make sure you have Python 3.6+ installed
2. Install and run Ollama locally:
   - Visit [Ollama's website](https://ollama.ai/) to download and install
   - Start the Ollama server (it should run on http://localhost:11434 by default)
   - Pull at least one model: `ollama pull llama3` (or any other model you prefer)

## Setup

Run the setup script to create the virtual environment and install dependencies:

```bash
./setup.sh
```

The setup script will:
- Check if a virtual environment exists and create one if needed
- Activate the virtual environment
- Install all required dependencies

## Running the Application

To run the interactive agent:

```bash
./run_agent.sh
```

You can customize the Ollama server URL by setting the OLLAMA_URL environment variable:

```bash
OLLAMA_URL=http://custom-ollama-server:11434 ./run_agent.sh
```

### MCP Client Integration

The application can integrate with MCP (Model Control Protocol) clients. You can configure MCP servers in a JSON configuration file:

```json
{
  "mcp-server-1": {
    "command": "python",
    "args": ["server.py"],
    "env": {
      "VAR1": "var1"
    }
  },
  "mcp-server-2": {
    "command": "node",
    "args": ["index.js"],
    "env": {
      "VAR2": "var2"
    }
  }
}
```

To run the application with MCP clients, specify the configuration file:

```bash
./run_agent.sh --mcp-config mcp_config.json
```

If you don't specify an MCP configuration file, the application will run without MCP tools.

When the application starts:
1. It will load the MCP client configuration and connect to the servers if requested
2. It will display a list of available Ollama models installed on your system
3. You can select which model to use by entering the corresponding number
4. The agent will then start with your selected model and MCP tools
5. You can interact with the agent by typing questions or commands

Type 'exit' or 'quit' to end the session.

## Project Structure

- `src/app/`: Application source code
  - `agent.py`: Interactive agent implementation with Ollama integration and model selection
  - `mcp_config.py`: MCP server configuration loader and manager
  - `mcp_client_manager.py`: Manager for creating and managing MCP clients
  - `banner.py`: Banner display for the application
  - `version.py`: Version information
- `src/tests/`: Test code
  - `test_mcp_client_manager.py`: Tests for the MCP client manager
- `mcp_config.json`: Configuration file for MCP servers
- `requirements.txt`: Python dependencies
- `setup.sh`: Script to set up the environment
- `run_agent.sh`: Script to run the agent
- `run_tests.sh`: Script to run the tests
- `.env.example`: Example environment variables
- `venv/`: Virtual environment directory (created during setup)

## About Strands with Ollama and MCP

This demo shows how to use Strands with Ollama, a platform for running large language models locally, and MCP clients for extended functionality. The example demonstrates how to:

1. Create an OllamaModel instance pointing to your local Ollama server
2. Select from available models installed on your Ollama server
3. Configure and manage MCP clients
4. Create an agent using the selected Ollama model and MCP tools
5. Ask the agent questions and process responses in an interactive session

## Customizing the Ollama Server

By default, the application connects to Ollama at http://localhost:11434. You can change this by:

1. Setting the OLLAMA_URL environment variable before running the script
2. Creating a `.env` file based on `.env.example` with your custom URL

## Development

To add more capabilities to your agent, modify the `agent.py` file. You can extend the example to:

- Add custom agent configurations
- Process responses in different ways
- Implement more complex conversation flows
- Integrate additional MCP clients and tools

To add more dependencies, update the `requirements.txt` file and run:

```bash
source venv/bin/activate
pip install -r requirements.txt
```
## Testing

To run the tests for the MCP client manager:

```bash
./run_tests.sh
```

This will run the unit tests to verify the functionality of the MCP client manager.
