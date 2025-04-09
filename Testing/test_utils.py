# test_utils.py
import sys
import os

def add_project_root_to_path():
    # Add the project root directory to sys.path for test-time imports.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
