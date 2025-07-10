#!/bin/bash

# Setup script for LangGraph + MCP experiment

echo "Setting up LangGraph + MCP experiment environment..."

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install ipykernel for Jupyter
python -m ipykernel install --user --name langgraph-mcp --display-name "LangGraph-MCP"

echo "Setup complete!"
echo ""
echo "To use this environment:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start Jupyter: jupyter notebook examples.ipynb"
echo "3. Make sure to select the 'LangGraph-MCP' kernel in Jupyter"
echo ""
echo "Note: You'll need to set OPENAI_API_KEY or another LLM provider API key"