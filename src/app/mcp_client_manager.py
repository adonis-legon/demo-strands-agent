#!/usr/bin/env python3
"""
MCP Client manager for creating and managing MCP clients
"""

from typing import Dict, List, Optional, Any

from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

from src.app.mcp_config import MCPConfigManager


class MCPClientManager:
    """Manager for creating and managing MCP clients"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = MCPConfigManager(config_path)
        self.clients: Dict[str, MCPClient] = {}
        
    def load_config(self) -> bool:
        """
        Load MCP server configurations
        
        Returns:
            bool: True if configuration was loaded successfully
        """
        return self.config_manager.load_config()
    
    def create_clients(self) -> Dict[str, MCPClient]:
        """
        Create MCP clients for all configured servers
        
        Returns:
            Dict mapping server names to MCPClient instances
        """
        for server_name, server_config in self.config_manager.get_all_servers().items():
            try:
                # Create a client for this server
                client = MCPClient(
                    lambda cmd=server_config.command, args=server_config.args, env=server_config.env: 
                    stdio_client(StdioServerParameters(
                        command=cmd,
                        args=args,
                        env=env
                    ))
                )
                
                # Store the client
                self.clients[server_name] = client
                print(f"Created MCP client for server '{server_name}'")
                
            except Exception as e:
                print(f"Error creating MCP client for server '{server_name}': {e}")
        
        return self.clients
    
    def get_client(self, server_name: str) -> Optional[MCPClient]:
        """
        Get MCP client for a specific server
        
        Args:
            server_name: Name of the server to get client for
            
        Returns:
            MCPClient or None if client not found
        """
        return self.clients.get(server_name)
    
    def get_all_clients(self) -> Dict[str, MCPClient]:
        """
        Get all MCP clients
        
        Returns:
            Dict mapping server names to MCPClient instances
        """
        return self.clients
    
    def list_all_tools(self) -> List[Any]:
        """
        List all tools from all MCP clients
        
        Returns:
            List of tools from all clients
        """
        all_tools = []
        for server_name, client in self.clients.items():
            try:
                tools = client.list_tools_sync()
                all_tools.extend(tools)
                print(f"Added {len(tools)} tools from '{server_name}'")
            except Exception as e:
                print(f"Error listing tools from '{server_name}': {e}")
        
        return all_tools
    
    def __enter__(self):
        """
        Context manager entry - connect all clients
        
        Returns:
            Self for context manager
        """
        for server_name, client in self.clients.items():
            try:
                client.__enter__()
            except Exception as e:
                print(f"Error connecting to MCP server '{server_name}': {e}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - disconnect all clients
        """
        for server_name, client in self.clients.items():
            try:
                client.__exit__(exc_type, exc_val, exc_tb)
            except Exception as e:
                print(f"Error disconnecting from MCP server '{server_name}': {e}")
