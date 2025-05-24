#!/usr/bin/env python3
"""
Unit tests for mcp_config.py (MCPConfigManager and MCPServerConfig)
"""
import os
import tempfile
import json
import unittest
from app.mcp_config import MCPConfigManager, MCPServerConfig

class TestMCPConfigManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file
        self.tempfile = tempfile.NamedTemporaryFile(delete=False, mode='w+', suffix='.json')
        self.config_data = {
            "server1": {
                "command": "/bin/echo",
                "args": ["hello"],
                "env": {"FOO": "bar"}
            },
            "server2": {
                "command": "/bin/ls",
                "args": ["-l"]
            }
        }
        json.dump(self.config_data, self.tempfile)
        self.tempfile.close()
        self.manager = MCPConfigManager(self.tempfile.name)

    def tearDown(self):
        os.unlink(self.tempfile.name)

    def test_load_config_success(self):
        self.assertTrue(self.manager.load_config())
        self.assertEqual(set(self.manager.list_servers()), {"server1", "server2"})

    def test_get_server_config(self):
        self.manager.load_config()
        config = self.manager.get_server_config("server1")
        self.assertIsInstance(config, MCPServerConfig)
        self.assertEqual(config.command, "/bin/echo")
        self.assertEqual(config.args, ["hello"])
        self.assertEqual(config.env, {"FOO": "bar"})

    def test_get_server_config_missing(self):
        self.manager.load_config()
        self.assertIsNone(self.manager.get_server_config("notfound"))

    def test_list_servers(self):
        self.manager.load_config()
        servers = self.manager.list_servers()
        self.assertIn("server1", servers)
        self.assertIn("server2", servers)

    def test_get_all_servers(self):
        self.manager.load_config()
        all_servers = self.manager.get_all_servers()
        self.assertIsInstance(all_servers, dict)
        self.assertIn("server1", all_servers)
        self.assertIsInstance(all_servers["server1"], MCPServerConfig)

    def test_load_config_invalid_json(self):
        # Write invalid JSON
        with open(self.tempfile.name, 'w') as f:
            f.write("{ invalid json }")
        self.assertFalse(self.manager.load_config())

    def test_load_config_missing_file(self):
        manager = MCPConfigManager("/tmp/does_not_exist.json")
        self.assertFalse(manager.load_config())

    def test_load_config_missing_fields(self):
        # Write config missing 'command' and 'args'
        bad_config = {"badserver": {"foo": "bar"}}
        with open(self.tempfile.name, 'w') as f:
            json.dump(bad_config, f)
        self.assertTrue(self.manager.load_config())
        self.assertNotIn("badserver", self.manager.list_servers())

if __name__ == "__main__":
    unittest.main()
