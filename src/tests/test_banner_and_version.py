#!/usr/bin/env python3
"""
Unit tests for banner.py and version.py
"""
import unittest
from app import banner, version
from unittest.mock import patch

class TestBanner(unittest.TestCase):
    def test_version_constant(self):
        # Check that VERSION is a non-empty string
        self.assertTrue(isinstance(version.VERSION, str))
        self.assertTrue(len(version.VERSION) > 0)

    @patch("builtins.print")
    def test_print_banner_prints(self, mock_print):
        banner.print_banner()
        # Should print at least once
        self.assertTrue(mock_print.called)
        # Should include the version string in the output
        printed_args = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
        self.assertIn(version.VERSION, printed_args)

if __name__ == "__main__":
    unittest.main()
