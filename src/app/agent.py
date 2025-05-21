#!/usr/bin/env python3
"""
Interactive demo for strands library with Ollama integration and MCP client support
"""

import os
import subprocess
import argparse
import readline
from strands import Agent
from strands.models.ollama import OllamaModel
from src.app.mcp_client_manager import MCPClientManager
from src.app.banner import print_banner
from src.app.version import VERSION

# Set up Ctrl+L to clear screen
def clear_screen(event=None):
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()  # Reprint the banner after clearing
    return None

# Configure readline to handle Ctrl+L
# Note: This direct binding may not work in all environments
# The setup_readline function provides a more robust approach
readline.parse_and_bind(r'"\C-l": clear_screen')

def get_ollama_models_with_tags():
    """Get list of available Ollama models with their tags by parsing ollama list output"""
    try:
        result = subprocess.run(['ollama', 'list'], 
                               capture_output=True, text=True, check=True)
        
        # Parse the output to extract model names and tags
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 1:  # Only header line or empty
            print("No Ollama models found")
            return [("llama3", "llama3", "latest")]  # Default fallback
            
        models = []
        # Skip the header line (first row)
        for line in lines[1:]:
            if line.strip():
                # Extract the model name (first column)
                parts = line.split()
                if parts:
                    full_model_name = parts[0]
                    # Handle model with tag
                    if ':' in full_model_name:
                        model_name, tag = full_model_name.split(':', 1)
                    else:
                        model_name = full_model_name
                        tag = "default"
                    
                    # Add model with its tag
                    models.append((full_model_name, model_name, tag))
                
        return models if models else [("llama3", "llama3", "latest")]
    except subprocess.SubprocessError as e:
        print(f"Error getting Ollama models: {e}")
        print("Falling back to default model (llama3)")
        return [("llama3", "llama3", "latest")]

def display_model_menu(models):
    """Display a menu for model selection"""
    print("\nAvailable Ollama models:")
    for i, (full_name, model_name, tag) in enumerate(models, 1):
        print(f"{i}. {model_name} (tag: {tag})")
    
    while True:
        try:
            choice = input("\nSelect a model (number): ")
            index = int(choice) - 1
            if 0 <= index < len(models):
                return models[index][0]  # Return the full model name with tag
            else:
                print(f"Please enter a number between 1 and {len(models)}")
        except ValueError:
            print("Please enter a valid number")

def setup_readline():
    """Configure readline for better input handling"""
    # Set up history file
    history_file = os.path.join(os.path.expanduser("~"), ".strands_agent_history")
    try:
        # Try to read history file if it exists
        if os.path.exists(history_file):
            try:
                readline.read_history_file(history_file)
                # Set history length
                readline.set_history_length(1000)
            except (FileNotFoundError, PermissionError) as e:
                print(f"Note: Could not read history file: {e}")
    except Exception as e:
        print(f"Note: History functionality limited: {e}")
    
    try:
        # Save history on exit
        import atexit
        atexit.register(readline.write_history_file, history_file)
    except Exception:
        pass
    
    # Set up Ctrl+L to clear screen
    try:
        readline.parse_and_bind(r'"\C-l": "clear\n"')
    except Exception:
        print("Note: Ctrl+L shortcut not available. Use 'clear' command instead.")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Strands Agent Demo with Ollama and MCP support")
    parser.add_argument("--mcp-config", type=str, 
                        help="Path to MCP server configuration file (optional)")
    return parser.parse_args()

def main():
    """Interactive session with a strands agent using Ollama and MCP clients"""
    args = parse_arguments()
    
    # Configure readline for better input handling
    setup_readline()
    
    # Display the banner with version
    print_banner()
    
    print("Starting Strands Agent Demo with Ollama and MCP support")
    
    # Initialize MCP client manager if config path is provided
    mcp_manager = None
    mcp_tools = []
    
    if args.mcp_config:
        print(f"Using MCP configuration from: {args.mcp_config}")
        mcp_manager = MCPClientManager(args.mcp_config)
        
        if not mcp_manager.load_config():
            print("Warning: Failed to load MCP configuration")
        else:
            print(f"Loaded MCP configuration with {len(mcp_manager.config_manager.list_servers())} servers")
            
            # Create MCP clients
            mcp_manager.create_clients()
    else:
        print("No MCP configuration provided. Running without MCP tools.")
    
    # Get Ollama URL from environment variable or use default
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    print(f"Using Ollama server at: {ollama_url}")
    
    # Get available models with tags and let user select one
    models = get_ollama_models_with_tags()
    selected_model = display_model_menu(models)
    print(f"Selected model: {selected_model}")
    
    # Create an Ollama model instance with the selected model
    ollama_model = OllamaModel(
        host=ollama_url,
        model_id=selected_model
    )
    
    # Create an agent using the Ollama model and MCP tools if available
    if mcp_manager:
        try:
            # Connect to MCP clients and get tools
            with mcp_manager:
                mcp_tools = mcp_manager.list_all_tools()
                print(f"Loaded {len(mcp_tools)} tools from MCP clients")
                
                # Create agent with MCP tools
                agent = Agent(model=ollama_model, tools=mcp_tools)
                
                print("Press Ctrl+C or Ctrl+D to exit at any time")
                print("\nStart asking questions!")
                
                # Interactive loop
                try:
                    while True:
                        # Get user input
                        try:
                            user_input = input("\nYou: ")
                        except EOFError:  # Handle Ctrl+D
                            print("\nExiting...")
                            break
                        
                        # Check if user wants to exit
                        if user_input.lower() in ['exit', 'quit']:
                            break
                        
                        # Handle clear screen command
                        if user_input.lower() in ['clear', 'cls']:
                            clear_screen()
                            continue
                        
                        # Show that the model is answering
                        print("\nThinking...")
                        
                        # Ask the agent - it will print the response automatically
                        agent(user_input)
                except KeyboardInterrupt:  # Handle Ctrl+C
                    print("\nExiting...")
        except Exception as e:
            print(f"Error using MCP clients: {e}")
            print("Falling back to basic agent without MCP tools")
            # Create basic agent without MCP tools
            agent = Agent(model=ollama_model)
            run_basic_agent(agent)
    else:
        # Create basic agent without MCP tools
        agent = Agent(model=ollama_model)
        run_basic_agent(agent)
    
    print("\nThank you for using Demo-Strands-Agent!")

def run_basic_agent(agent):
    """Run a basic agent interaction loop"""
    print("Press Ctrl+C or Ctrl+D to exit at any time")
    print("\nStart asking questions!")
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("\nYou: ")
            except EOFError:  # Handle Ctrl+D
                print("\nExiting...")
                break
                
            # Check if user wants to exit
            if user_input.lower() in ['exit', 'quit']:
                break
                
            # Handle clear screen command
            if user_input.lower() in ['clear', 'cls']:
                clear_screen()
                continue
            
            # Show that the model is answering
            print("\nThinking...")
            
            # Ask the agent - it will print the response automatically
            agent(user_input)
    except KeyboardInterrupt:  # Handle Ctrl+C
        print("\nExiting...")
        
    print("\nThank you for using Demo-Strands-Agent!")
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        print("\nThank you for using Demo-Strands-Agent!")
    except EOFError:
        print("\nExiting...")
        print("\nThank you for using Demo-Strands-Agent!")
