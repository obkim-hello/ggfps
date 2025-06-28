#!/bin/bash
# Emergency stop script for GLFPS
echo "🚨 Emergency stopping GLFPS..."
pkill -f "python.*simple_detector"
pkill -f "python.*glfps"
echo "✅ GLFPS processes stopped"
