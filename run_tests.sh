#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Add src directory to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the tests
echo "Running tests..."
python -m src.tests.test_mcp_client_manager

# Deactivate virtual environment when done
deactivate

echo "All tests completed."
