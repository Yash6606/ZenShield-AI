import sys
import os

# Add the parent directory to sys.path so app can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app
