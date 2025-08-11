"""
Streamlit App Entry Point for Cloud Deployment
Direct dashboard launch without CLI dependencies
"""

import sys
import os
from pathlib import Path

# Set up environment and paths first
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

# Set deployment environment variables
os.environ['STREAMLIT_DEPLOYMENT'] = 'true'
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'false'
os.environ['STREAMLIT_GLOBAL_DEVELOPMENT_MODE'] = 'false'

# Handle port assignment
if 'PORT' in os.environ:
    os.environ['STREAMLIT_SERVER_PORT'] = os.environ['PORT']

# Direct import and execution
try:
    # Import all required modules
    import streamlit as st
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Simple health check
    st.set_page_config(
        page_title="Vehicle Registration Dashboard",
        page_icon="🚗",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Try to import our dashboard
    try:
        from src.dashboard.app import main as dashboard_main
        dashboard_main()
    except ImportError as import_error:
        # Fallback to simple dashboard if import fails
        st.title("🚗 Vehicle Registration Dashboard")
        st.error(f"Import error: {import_error}")
        st.info("Running in fallback mode with sample data...")
        
        # Create simple sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        sample_data = []
        
        for date in dates:
            sample_data.append({
                'date': date,
                'registrations': np.random.randint(100, 1000),
                'category': np.random.choice(['Car', 'Bike', 'Truck', 'Bus'])
            })
        
        df = pd.DataFrame(sample_data)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Registrations", f"{df['registrations'].sum():,}")
        with col2:
            st.metric("Average Daily", f"{df['registrations'].mean():.0f}")
        with col3:
            st.metric("Categories", df['category'].nunique())
        
        st.line_chart(df.set_index('date')['registrations'])
        st.success("✅ Fallback dashboard is working!")
        
except Exception as critical_error:
    # Last resort fallback
    import streamlit as st
    st.title("🚗 Vehicle Registration Dashboard")
    st.error(f"Critical error: {critical_error}")
    st.info("The dashboard encountered an error but the deployment is working.")
    st.success("✅ Streamlit is running successfully!")
