#!/usr/bin/env python3
"""
Unit tests for mcp_client_manager.py (MCPClientManager)
"""
import unittest
from unittest.mock import MagicMock, patch
from app.mcp_client_manager import MCPClientManager

class TestMCPClientManager(unittest.TestCase):
    def setUp(self):
        # Mock MCPConfigManager
        self.mock_config_manager = MagicMock()
        self.mock_config_manager.list_servers.return_value = ["server1", "server2"]
        # Mock server configs
        mock_server_config1 = MagicMock()
        mock_server_config1.command = "/bin/echo"
        mock_server_config1.args = ["hello"]
        mock_server_config1.env = {"FOO": "bar"}
        mock_server_config2 = MagicMock()
        mock_server_config2.command = "/bin/ls"
        mock_server_config2.args = ["-l"]
        mock_server_config2.env = {"BAR": "baz"}
        self.mock_config_manager.get_server_config.side_effect = lambda name: {
            "server1": mock_server_config1,
            "server2": mock_server_config2
        }[name]

    @patch("app.mcp_client_manager.MCPClient")
    @patch("app.mcp_client_manager.stdio_client")
    @patch("app.mcp_client_manager.StdioServerParameters")
    def test_create_clients_success(self, mock_params, mock_stdio_client, mock_mcp_client):
        # Setup mocks
        mock_mcp_client.side_effect = lambda func: f"MCPClient({func})"
        manager = MCPClientManager(self.mock_config_manager)
        clients = manager.create_clients()
        self.assertEqual(len(clients), 2)
        self.assertTrue(all(str(c).startswith("MCPClient(") for c in clients))
        self.mock_config_manager.list_servers.assert_called_once()
        self.assertEqual(self.mock_config_manager.get_server_config.call_count, 2)

    def test_create_clients_no_config_manager(self):
        manager = MCPClientManager(None)
        with self.assertRaises(Exception) as ctx:
            manager.create_clients()
        self.assertIn("MCPConfigManager is missing", str(ctx.exception))

    def test_create_clients_missing_server_config(self):
        self.mock_config_manager.list_servers.return_value = ["server1"]
        self.mock_config_manager.get_server_config.side_effect = lambda name: None
        manager = MCPClientManager(self.mock_config_manager)
        with self.assertRaises(Exception) as ctx:
            manager.create_clients()
        self.assertIn("Server config for server1 not found", str(ctx.exception))

    def test_create_clients_missing_command_or_args(self):
        bad_config = MagicMock()
        bad_config.command = None
        bad_config.args = None
        bad_config.env = {"FOO": "bar"}
        self.mock_config_manager.list_servers.return_value = ["server1"]
        self.mock_config_manager.get_server_config.side_effect = lambda name: bad_config
        manager = MCPClientManager(self.mock_config_manager)
        with self.assertRaises(Exception) as ctx:
            manager.create_clients()
        self.assertIn("missing 'command' or 'args'", str(ctx.exception))

    def test_create_clients_missing_env(self):
        bad_config = MagicMock()
        bad_config.command = "/bin/echo"
        bad_config.args = ["hello"]
        bad_config.env = None
        self.mock_config_manager.list_servers.return_value = ["server1"]
        self.mock_config_manager.get_server_config.side_effect = lambda name: bad_config
        manager = MCPClientManager(self.mock_config_manager)
        with self.assertRaises(Exception) as ctx:
            manager.create_clients()
        self.assertIn("missing 'env'", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
