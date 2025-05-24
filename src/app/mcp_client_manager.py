#!/usr/bin/env python3
"""
MCP Client manager for creating and managing MCP clients
"""

from typing import Optional

from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient
from strands import Agent

from .mcp_config import MCPConfigManager


class MCPClientManager:
    """Manager for creating and managing MCP clients"""
    
    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager
    
    def create_clients(self) -> Agent:
        """
        Create MCPClient instances based on the loaded configurations.
        Each config should provide 'command', 'args', and 'env' keys.
        """
        if not self.config_manager:
            raise Exception("MCPConfigManager is missing. Cannot create clients.")

        clients = []
        for server_name in self.config_manager.list_servers():
            server_config = self.config_manager.get_server_config(server_name)
            if not server_config:
                raise Exception(f"Server config for {server_name} not found.")
            if not server_config.command or not server_config.args:
                raise Exception(f"Server config for {server_name} is missing 'command' or 'args'.")
            if server_config.env is None:
                server_config.env = {}
            # Create a new MCPClient instance for each server configuration
            clients.append(MCPClient(lambda: stdio_client(StdioServerParameters(command=server_config.command, args=server_config.args, env=server_config.env))))
        return clients