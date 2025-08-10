"""
Streamlit App Entry Point for Cloud Deployment
"""

import sys
from pathlib import Path
import os

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

# Set environment variables for deployment
os.environ['STREAMLIT_DEPLOYMENT'] = 'true'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'

# Import and run the main dashboard directly
if __name__ == "__main__":
    from src.dashboard.app import main
    main()
