#!/usr/bin/env python3
"""
Test cases for the MCP Client Manager
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.app.mcp_client_manager import MCPClientManager


class TestMCPClientManager(unittest.TestCase):
    """Test cases for the MCP Client Manager"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a temporary test config file
        self.test_config_path = "test_mcp_config.json"
        self.test_config = {
            "test-server-1": {
                "command": "python",
                "args": ["server1.py"],
                "env": {
                    "TEST_VAR1": "value1"
                }
            },
            "test-server-2": {
                "command": "node",
                "args": ["server2.js"],
                "env": {
                    "TEST_VAR2": "value2"
                }
            }
        }
        
        # Write the test config to a file
        with open(self.test_config_path, "w") as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove the temporary test config file
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_load_config(self):
        """Test loading configuration from file"""
        manager = MCPClientManager(self.test_config_path)
        result = manager.load_config()
        
        self.assertTrue(result)
        self.assertEqual(len(manager.config_manager.list_servers()), 2)
        self.assertIn("test-server-1", manager.config_manager.list_servers())
        self.assertIn("test-server-2", manager.config_manager.list_servers())
    
    @patch('src.app.mcp_client_manager.MCPClient')
    @patch('src.app.mcp_client_manager.stdio_client')
    def test_create_clients(self, mock_stdio_client, mock_mcp_client):
        """Test creating MCP clients"""
        # Set up mocks
        mock_client_instance = MagicMock()
        mock_mcp_client.return_value = mock_client_instance
        
        # Create manager and load config
        manager = MCPClientManager(self.test_config_path)
        manager.load_config()
        
        # Create clients
        clients = manager.create_clients()
        
        # Verify results
        self.assertEqual(len(clients), 2)
        self.assertIn("test-server-1", clients)
        self.assertIn("test-server-2", clients)
        
        # Verify MCPClient was called twice
        self.assertEqual(mock_mcp_client.call_count, 2)
    
    @patch('src.app.mcp_client_manager.MCPClient')
    @patch('src.app.mcp_client_manager.stdio_client')
    def test_context_manager(self, mock_stdio_client, mock_mcp_client):
        """Test context manager functionality"""
        # Set up mocks
        mock_client1 = MagicMock()
        mock_client2 = MagicMock()
        
        # Make MCPClient return different instances for different calls
        mock_mcp_client.side_effect = [mock_client1, mock_client2]
        
        # Create manager and load config
        manager = MCPClientManager(self.test_config_path)
        manager.load_config()
        manager.create_clients()
        
        # Use context manager
        with manager:
            pass
        
        # Verify __enter__ and __exit__ were called on each client
        mock_client1.__enter__.assert_called_once()
        mock_client1.__exit__.assert_called_once()
        mock_client2.__enter__.assert_called_once()
        mock_client2.__exit__.assert_called_once()
    
    @patch('src.app.mcp_client_manager.MCPClient')
    @patch('src.app.mcp_client_manager.stdio_client')
    def test_list_all_tools(self, mock_stdio_client, mock_mcp_client):
        """Test listing all tools from clients"""
        # Set up mocks
        mock_client1 = MagicMock()
        mock_client1.list_tools_sync.return_value = ["tool1", "tool2"]
        
        mock_client2 = MagicMock()
        mock_client2.list_tools_sync.return_value = ["tool3", "tool4"]
        
        # Make MCPClient return different instances for different calls
        mock_mcp_client.side_effect = [mock_client1, mock_client2]
        
        # Create manager and load config
        manager = MCPClientManager(self.test_config_path)
        manager.load_config()
        manager.create_clients()
        
        # List all tools
        tools = manager.list_all_tools()
        
        # Verify results
        self.assertEqual(len(tools), 4)
        self.assertIn("tool1", tools)
        self.assertIn("tool2", tools)
        self.assertIn("tool3", tools)
        self.assertIn("tool4", tools)
        
        # Verify list_tools_sync was called on each client
        mock_client1.list_tools_sync.assert_called_once()
        mock_client2.list_tools_sync.assert_called_once()


if __name__ == "__main__":
    unittest.main()
