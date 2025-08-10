"""
Dashboard UI Components

This module contains reusable UI components for the Streamlit dashboard.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Tuple, Optional


def create_sidebar_filters(data: pd.DataFrame) -> Dict:
    """
    Create sidebar filters for the dashboard.
    
    Args:
        data: DataFrame containing vehicle registration data
        
    Returns:
        Dictionary with filter selections
    """
    st.sidebar.title("🔧 Filters")
    
    # Date range filter
    min_date = data['date'].min().date()
    max_date = data['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Select the date range for analysis"
    )
    
    # Vehicle category filter
    categories = sorted(data['vehicle_category'].unique())
    selected_categories = st.sidebar.multiselect(
        "🚗 Vehicle Categories",
        options=categories,
        default=categories,
        help="Select vehicle categories to include"
    )
    
    # Manufacturer filter
    manufacturers = sorted(data['manufacturer'].unique())
    selected_manufacturers = st.sidebar.multiselect(
        "🏭 Manufacturers",
        options=manufacturers,
        default=manufacturers[:10] if len(manufacturers) > 10 else manufacturers,
        help="Select manufacturers to include (default: top 10)"
    )
    
    # Additional filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Advanced Options")
    
    # Minimum registration threshold
    min_registrations = st.sidebar.number_input(
        "Minimum Registrations",
        min_value=0,
        value=0,
        step=100,
        help="Filter out records below this threshold"
    )
    
    # Growth threshold for highlighting
    growth_threshold = st.sidebar.slider(
        "Growth Highlight Threshold (%)",
        min_value=0.0,
        max_value=50.0,
        value=10.0,
        step=1.0,
        help="Highlight growth rates above this threshold"
    )
    
    return {
        'date_range': date_range,
        'categories': selected_categories,
        'manufacturers': selected_manufacturers,
        'min_registrations': min_registrations,
        'growth_threshold': growth_threshold
    }


def display_kpis(data: pd.DataFrame, title: str = "Key Performance Indicators") -> None:
    """
    Display key performance indicators in a grid layout.
    
    Args:
        data: DataFrame containing vehicle registration data
        title: Title for the KPI section
    """
    st.subheader(title)
    
    # Calculate KPIs
    total_registrations = data['registrations'].sum()
    avg_monthly = data.groupby('year_month')['registrations'].sum().mean()
    unique_manufacturers = data['manufacturer'].nunique()
    unique_categories = data['vehicle_category'].nunique()
    
    # Latest month data
    latest_month = data['year_month'].max()
    latest_registrations = data[data['year_month'] == latest_month]['registrations'].sum()
    
    # Previous month for comparison
    months = sorted(data['year_month'].unique())
    if len(months) > 1:
        prev_month = months[-2]
        prev_registrations = data[data['year_month'] == prev_month]['registrations'].sum()
        month_change = ((latest_registrations - prev_registrations) / prev_registrations * 100) if prev_registrations > 0 else 0
    else:
        month_change = 0
    
    # Display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Registrations",
            f"{total_registrations:,}",
            help="Total vehicle registrations in selected period"
        )
    
    with col2:
        st.metric(
            "Latest Month",
            f"{latest_registrations:,}",
            delta=f"{month_change:+.1f}%" if month_change != 0 else None,
            help=f"Registrations in {latest_month}"
        )
    
    with col3:
        st.metric(
            "Avg Monthly",
            f"{avg_monthly:,.0f}",
            help="Average registrations per month"
        )
    
    with col4:
        st.metric(
            "Active Manufacturers",
            f"{unique_manufacturers}",
            help="Number of manufacturers with registrations"
        )


def create_growth_metrics_section(yoy_data: pd.DataFrame, qoq_data: pd.DataFrame) -> None:
    """
    Create a section displaying growth metrics with visualizations.
    
    Args:
        yoy_data: DataFrame with YoY growth data
        qoq_data: DataFrame with QoQ growth data
    """
    st.subheader("📈 Growth Metrics")
    
    # Create tabs for different growth metrics
    tab1, tab2 = st.tabs(["Year-over-Year", "Quarter-over-Quarter"])
    
    with tab1:
        if not yoy_data.empty:
            display_growth_summary(yoy_data, 'yoy_growth_pct', "YoY Growth")
        else:
            st.info("Insufficient data for YoY analysis")
    
    with tab2:
        if not qoq_data.empty:
            display_growth_summary(qoq_data, 'qoq_growth_pct', "QoQ Growth")
        else:
            st.info("Insufficient data for QoQ analysis")


def display_growth_summary(data: pd.DataFrame, growth_col: str, title: str) -> None:
    """
    Display growth summary with top performers and visualizations.
    
    Args:
        data: DataFrame with growth data
        growth_col: Column name containing growth percentages
        title: Title for the section
    """
    # Filter out infinite and NaN values
    clean_data = data[data[growth_col].notna() & (data[growth_col] != float('inf')) & (data[growth_col] != float('-inf'))]
    
    if clean_data.empty:
        st.warning(f"No valid {title} data available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top performers
        st.markdown(f"**🚀 Top {title} Performers**")
        top_performers = clean_data.nlargest(5, growth_col)[
            ['manufacturer', 'vehicle_category', growth_col]
        ].copy()
        
        # Format growth percentages
        top_performers[growth_col] = top_performers[growth_col].round(2)
        top_performers = top_performers.rename(columns={growth_col: f'{title} (%)'})
        
        # Style the dataframe
        styled_df = top_performers.style.format({f'{title} (%)': '{:.1f}%'})
        st.dataframe(styled_df, hide_index=True)
    
    with col2:
        # Growth distribution
        st.markdown(f"**📊 {title} Distribution**")
        
        fig = px.histogram(
            clean_data,
            x=growth_col,
            nbins=30,
            title=f"{title} Distribution",
            labels={growth_col: f"{title} (%)"},
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.update_layout(
            height=300,
            showlegend=False,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)


def create_filter_summary(filters: Dict) -> None:
    """
    Display a summary of applied filters.
    
    Args:
        filters: Dictionary containing filter selections
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Filter Summary")
    
    # Date range
    if len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        st.sidebar.write(f"📅 **Date:** {start_date} to {end_date}")
    
    # Categories
    if filters['categories']:
        categories_str = ", ".join(filters['categories'])
        st.sidebar.write(f"🚗 **Categories:** {categories_str}")
    
    # Manufacturers count
    manufacturer_count = len(filters['manufacturers'])
    st.sidebar.write(f"🏭 **Manufacturers:** {manufacturer_count} selected")
    
    # Thresholds
    if filters['min_registrations'] > 0:
        st.sidebar.write(f"📊 **Min Registrations:** {filters['min_registrations']:,}")


def create_data_quality_info(data: pd.DataFrame) -> None:
    """
    Display data quality information.
    
    Args:
        data: DataFrame to analyze
    """
    with st.expander("ℹ️ Data Quality Information"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{len(data):,}")
            st.metric("Date Range", f"{(data['date'].max() - data['date'].min()).days} days")
        
        with col2:
            missing_values = data.isnull().sum().sum()
            st.metric("Missing Values", f"{missing_values:,}")
            
            zero_registrations = (data['registrations'] == 0).sum()
            st.metric("Zero Registrations", f"{zero_registrations:,}")
        
        with col3:
            duplicate_records = data.duplicated().sum()
            st.metric("Duplicate Records", f"{duplicate_records:,}")
            
            data_completeness = ((len(data) - missing_values) / len(data) * 100) if len(data) > 0 else 0
            st.metric("Data Completeness", f"{data_completeness:.1f}%")


def create_export_section(data: pd.DataFrame, growth_data: Optional[pd.DataFrame] = None) -> None:
    """
    Create data export section with download buttons.
    
    Args:
        data: Main dataset to export
        growth_data: Optional growth analysis data
    """
    st.subheader("💾 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export filtered data
        csv_data = data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv_data,
            file_name=f"vehicle_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download the currently filtered dataset"
        )
    
    with col2:
        # Export summary stats
        summary_stats = data.groupby(['vehicle_category', 'manufacturer']).agg({
            'registrations': ['sum', 'mean', 'count']
        }).round(2)
        
        summary_csv = summary_stats.to_csv()
        st.download_button(
            label="📊 Download Summary Stats",
            data=summary_csv,
            file_name=f"summary_stats_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            help="Download aggregated statistics"
        )
    
    with col3:
        # Export growth data if available
        if growth_data is not None and not growth_data.empty:
            growth_csv = growth_data.to_csv(index=False)
            st.download_button(
                label="📈 Download Growth Analysis",
                data=growth_csv,
                file_name=f"growth_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                help="Download growth analysis data"
            )
        else:
            st.button(
                "📈 Growth Analysis",
                disabled=True,
                help="No growth data available"
            )
