#!/usr/bin/env python3
"""
MCP Server configuration loader and manager
"""

import json
import os
from typing import Dict, List, Optional


class MCPServerConfig:
    """Class representing a single MCP server configuration"""
    
    def __init__(self, name: str, command: str, args: List[str], env: Dict[str, str]):
        self.name = name
        self.command = command
        self.args = args
        self.env = env

    def __repr__(self) -> str:
        return f"MCPServerConfig(name={self.name}, command={self.command}, args={self.args})"


class MCPConfigManager:
    """Manager for MCP server configurations"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "mcp_config.json")
        self.servers: Dict[str, MCPServerConfig] = {}
        
    def load_config(self) -> bool:
        """
        Load MCP server configurations from the JSON file
        
        Returns:
            bool: True if configuration was loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_path):
                print(f"MCP configuration file not found: {self.config_path}")
                return False
                
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Clear existing configurations
            self.servers.clear()
            
            # Process each server configuration
            for server_name, server_config in config_data.items():
                if not all(key in server_config for key in ['command', 'args']):
                    print(f"Warning: Invalid configuration for server '{server_name}'. "
                          f"Missing required fields.")
                    continue
                
                # Create server config object
                self.servers[server_name] = MCPServerConfig(
                    name=server_name,
                    command=server_config['command'],
                    args=server_config['args'],
                    env=server_config.get('env', {})
                )
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error parsing MCP configuration file: {e}")
            return False
        except Exception as e:
            print(f"Error loading MCP configuration: {e}")
            return False
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """
        Get configuration for a specific server
        
        Args:
            server_name: Name of the server to get configuration for
            
        Returns:
            MCPServerConfig or None if server not found
        """
        return self.servers.get(server_name)
    
    def list_servers(self) -> List[str]:
        """
        Get list of configured server names
        
        Returns:
            List of server names
        """
        return list(self.servers.keys())
    
    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """
        Get all server configurations
        
        Returns:
            Dictionary of server configurations
        """
        return self.servers
