import sys
import os

# Add the project root directory to sys.path
# This allows importing main.py and other modules from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel looks for 'app'
