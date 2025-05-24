#!/usr/bin/env python3
"""
Unit tests for agent.py (main logic, argument parsing, and agent loop)
"""
import unittest
from unittest.mock import patch, MagicMock, call
from app import agent
import sys

class TestAgentMain(unittest.TestCase):
    @patch("app.agent.parse_arguments")
    @patch("app.agent.setup_readline")
    @patch("app.agent.print_banner")
    @patch("app.agent.MCPConfigManager")
    @patch("app.agent.MCPClientManager")
    @patch("app.agent.get_ollama_models_with_tags")
    @patch("app.agent.display_model_menu")
    @patch("app.agent.OllamaModel")
    @patch("app.agent.SlidingWindowConversationManager")
    @patch("app.agent.Agent")
    @patch("app.agent.run_basic_agent")
    def test_main_happy_path(self, mock_run_basic_agent, mock_Agent, mock_SlidingWindowConversationManager,
                            mock_OllamaModel, mock_display_model_menu, mock_get_ollama_models_with_tags,
                            mock_MCPClientManager, mock_MCPConfigManager, mock_print_banner, mock_setup_readline, mock_parse_arguments):
        # Setup mocks
        mock_args = MagicMock()
        mock_args.mcp_config = None
        mock_args.window_size = 5
        mock_parse_arguments.return_value = mock_args
        mock_MCPConfigManager.return_value.load_config.return_value = True
        mock_manager = MagicMock()
        mock_client = MagicMock()
        mock_client.list_tools_sync.return_value = ["tool1", "tool2"]
        mock_manager.create_clients.return_value = [mock_client]
        mock_MCPClientManager.return_value = mock_manager
        mock_get_ollama_models_with_tags.return_value = [("llama3:latest", "llama3", "latest")]
        mock_display_model_menu.return_value = "llama3:latest"
        mock_OllamaModel.return_value = MagicMock()
        mock_SlidingWindowConversationManager.return_value = MagicMock()
        mock_Agent.return_value = MagicMock()
        # Run main
        agent.main()
        mock_print_banner.assert_called()
        mock_run_basic_agent.assert_called()
        mock_Agent.assert_called()
        mock_manager.create_clients.assert_called()
        mock_client.list_tools_sync.assert_called()

    @patch("app.agent.input", side_effect=["exit"])
    def test_run_basic_agent_exit(self, mock_input):
        mock_agent = MagicMock()
        agent.run_basic_agent(mock_agent)
        mock_agent.assert_not_called()  # Should not call agent if user types 'exit' immediately

    @patch("app.agent.input", side_effect=["clear", "exit"])
    @patch("app.agent.clear_screen")
    def test_run_basic_agent_clear(self, mock_clear_screen, mock_input):
        mock_agent = MagicMock()
        agent.run_basic_agent(mock_agent)
        mock_clear_screen.assert_called_once()
        mock_agent.assert_not_called()  # Should not call agent for 'clear', nor for 'exit'

    @patch("app.agent.input", side_effect=["hello", "exit"])
    def test_run_basic_agent_ask(self, mock_input):
        mock_agent = MagicMock()
        agent.run_basic_agent(mock_agent)
        mock_agent.assert_called_once_with("hello")

    @patch("app.agent.input", side_effect=KeyboardInterrupt)
    def test_run_basic_agent_keyboard_interrupt(self, mock_input):
        mock_agent = MagicMock()
        # Should not raise, should print Exiting
        agent.run_basic_agent(mock_agent)
        mock_agent.assert_not_called()

    @patch("app.agent.input", side_effect=EOFError)
    def test_run_basic_agent_eof(self, mock_input):
        mock_agent = MagicMock()
        # Should not raise, should print Exiting
        agent.run_basic_agent(mock_agent)
        mock_agent.assert_not_called()

if __name__ == "__main__":
    unittest.main()
