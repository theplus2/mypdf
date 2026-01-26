#!/usr/bin/env python3
"""
MyPDF Library - PDF Book Management Application
Main entry point
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    main()