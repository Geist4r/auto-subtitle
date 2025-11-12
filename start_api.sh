#!/bin/bash

echo "Installing API dependencies..."
pip install -r requirements-api.txt

echo ""
echo "Starting API server..."
echo "API will be available at: http://localhost:8000"
echo "API docs will be at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m auto_subtitle.api
