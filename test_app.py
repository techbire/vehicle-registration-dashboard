"""
Simple Test Dashboard - Minimal version for deployment testing
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Vehicle Dashboard Test",
    page_icon="🚗",
    layout="wide"
)

def main():
    """Simple test dashboard."""
    
    st.title("🚗 Vehicle Registration Dashboard - Test Version")
    st.write("✅ Dashboard is running successfully!")
    
    # Create simple test data
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    test_data = []
    for date in dates:
        test_data.append({
            'date': date,
            'registrations': np.random.randint(100, 1000),
            'category': np.random.choice(['Car', 'Bike', 'Truck'])
        })
    
    df = pd.DataFrame(test_data)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Registrations", f"{df['registrations'].sum():,}")
    
    with col2:
        st.metric("Average Daily", f"{df['registrations'].mean():.0f}")
    
    with col3:
        st.metric("Peak Day", f"{df['registrations'].max():,}")
    
    # Simple chart
    st.line_chart(df.set_index('date')['registrations'])
    
    # Show data
    if st.checkbox("Show Raw Data"):
        st.dataframe(df)
    
    st.success("🎉 Test dashboard working perfectly!")

if __name__ == "__main__":
    main()
