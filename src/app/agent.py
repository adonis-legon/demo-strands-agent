#!/usr/bin/env python3
"""
Interactive demo for strands library with Ollama integration and MCP client support
"""

import os
import subprocess
import argparse
import readline
import contextlib
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import current_time
from .mcp_client_manager import MCPClientManager
from .mcp_config import MCPConfigManager
from .banner import print_banner

# Set up Ctrl+L to clear screen
def clear_screen(event=None):
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()  # Reprint the banner after clearing
    return None

# Configure readline to handle Ctrl+L
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
    parser.add_argument("--window-size", type=int, default=10,
                        help="Size of the conversation history window (default: 10)")
    return parser.parse_args()

def main():
    """Interactive session with a strands agent using Ollama and MCP clients"""
    args = parse_arguments()
    
    # Configure readline for better input handling
    setup_readline()
    
    # Display the banner with version
    print_banner()
    
    print("Starting Strands Agent Demo with Ollama and MCP support")
    print(f"Conversation history window size: {args.window_size}")
    
    # Load MCP configuration if provided
    mcp_config_manager = MCPConfigManager(args.mcp_config)
    mcp_config_manager.load_config()
    
    # Create MCP client manager
    mcp_manager = MCPClientManager(mcp_config_manager)
    
    # Get Ollama URL from environment variable or use default
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    print(f"Using Ollama server at: {ollama_url}")
    
    # Get available models with tags and let user select one
    models = get_ollama_models_with_tags()
    selected_model = display_model_menu(models)
    print(f"Selected model: {selected_model}")
    
    # Create an Ollama model instance with the selected model
    model = OllamaModel(
        host=ollama_url,
        model_id=selected_model
    )
    
    # Create a conversation manager with the specified window size
    conversation_manager = SlidingWindowConversationManager(window_size=args.window_size)
    
    # Create mcp clients
    print("Creating MCP clients...")
    clients = mcp_manager.create_clients()
    
    agent = Agent(model=model, conversation_manager=conversation_manager, tools=[current_time]) #new
    with contextlib.ExitStack() as stack:
        # tools = []
        for client in clients:
            stack.enter_context(client)

            # List the tools available on the MCP server...
            mcp_tools = client.list_tools_sync() #new
            print(f"Available tools: {[tool.tool_name for tool in mcp_tools]}") #new
            
            agent.tool_registry.process_tools(mcp_tools)
            # tools.extend(client.list_tools_sync())
            
        # agent = Agent(model=model, tools=tools, conversation_manager=conversation_manager)
    
        # Run the interactive loop
        print("Press Ctrl+C or Ctrl+D to exit at any time")
        print("\nStart asking questions!")
        run_basic_agent(agent)
        
    print("\nThank you for using Demo-Strands-Agent!")

def run_basic_agent(agent):
    """Run a basic agent interaction loop"""
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

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        print("\nThank you for using Demo-Strands-Agent!")
    except EOFError:
        print("\nExiting...")
        print("\nThank you for using Demo-Strands-Agent!")
