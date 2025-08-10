"""
Production Entry Point - Bypasses Streamlit file watching entirely
"""

import sys
import os
from pathlib import Path

# Disable all file watching before any imports
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# Let the platform handle port assignment
if 'PORT' in os.environ:
    os.environ['STREAMLIT_SERVER_PORT'] = os.environ['PORT']

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import streamlit with file watching disabled
import streamlit as st

# Configure streamlit programmatically
st.set_page_config(
    page_title="Vehicle Registration Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import and run our app
from src.dashboard.app import main

if __name__ == "__main__":
    main()
