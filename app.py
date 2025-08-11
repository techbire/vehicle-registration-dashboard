"""
Direct Streamlit entry point for deployment.
This file serves as the main entry point for cloud deployment platforms.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Import and run the main dashboard
from src.dashboard.app import main

if __name__ == "__main__":
    main()
