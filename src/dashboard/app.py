"""
Main Streamlit Dashboard Application

This is the main entry point for the vehicle registration dashboard.
Run with: streamlit run src/dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data.scraper import VahanDataScraper
from data.processor import VehicleDataProcessor
from dashboard.components import (
    create_sidebar_filters, 
    display_kpis, 
    create_growth_metrics_section
)
from dashboard.charts import (
    create_trend_chart,
    create_growth_chart,
    create_market_share_chart,
    create_category_comparison_chart
)

# Page configuration
st.set_page_config(
    page_title="Vehicle Registration Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .growth-positive {
        color: #28a745;
        font-weight: bold;
    }
    .growth-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and cache vehicle registration data."""
    try:
        scraper = VahanDataScraper()
        
        data = scraper.load_sample_data()
        
        if data.empty:
            # Generate sample data if none exists
            data = scraper.generate_sample_data()
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        try:
            # Fallback: create minimal sample data directly
            import pandas as pd
            import numpy as np
            from datetime import datetime, timedelta
            
            # Create 30 days of sample data
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=30),
                end=datetime.now(),
                freq='D'
            )
            
            sample_data = []
            categories = ['Two Wheeler', 'Car', 'Commercial Vehicle', 'Bus', 'Truck']
            manufacturers = ['Maruti', 'Hyundai', 'Tata', 'Honda', 'Toyota']
            
            for date in dates:
                for category in categories:
                    for manufacturer in manufacturers:
                        registrations = np.random.randint(50, 500)
                        sample_data.append({
                            'date': date,
                            'category': category,
                            'manufacturer': manufacturer,
                            'registrations': registrations,
                            'state': 'Sample State',
                            'district': 'Sample District'
                        })
            
            return pd.DataFrame(sample_data)
        except Exception as fallback_error:
            st.error(f"Critical error: {fallback_error}")
            return pd.DataFrame()


def main():
    """Main dashboard application."""

    # Header
    st.markdown('<h1 class="main-header">🚗 Vehicle Registration Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Interactive analytics dashboard for vehicle registration data from Vahan portal
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading vehicle registration data..."):
        raw_data = load_data()
    
    if raw_data.empty:
        st.error("No data available. Please check the data source.")
        return
    
    # Initialize processor
    processor = VehicleDataProcessor(raw_data)
    
    # Sidebar filters
    st.sidebar.title("📊 Dashboard Filters")
    
    # Date range selection with quick options
    min_date = processor.processed_data['date'].min().date()
    max_date = processor.processed_data['date'].max().date()
    
    st.sidebar.subheader("Select Date Range")
    
    # Display available data range
    st.sidebar.caption(f"📊 Available data: {min_date} to {max_date}")
    st.sidebar.caption("💡 Date ranges calculate from the last available data date, not today")
    
    # Quick date range options
    date_option = st.sidebar.selectbox(
        "Quick Date Selection",
        options=["All Time", "Past Week", "Past Month", "Past 3 Months", 
                "Past 6 Months", "Past Year", "Past 2 Years", "Custom Range"],
        index=0,  # Default to "All Time"
        help="Select a predefined range or choose 'Custom Range' for manual selection"
    )
    
    # Calculate date range based on selection
    if date_option == "Custom Range":
        st.sidebar.warning("⚠️ Custom dates must be within the available data range")
        date_range = st.sidebar.date_input(
            "Custom Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help=f"Select dates between {min_date} and {max_date}"
        )
    else:
        # Calculate quick date ranges based on data availability (from max_date backwards)
        if date_option == "Past Week":
            start_date = max_date - timedelta(days=7)
        elif date_option == "Past Month":
            start_date = max_date - timedelta(days=30)
        elif date_option == "Past 3 Months":
            start_date = max_date - timedelta(days=90)
        elif date_option == "Past 6 Months":
            start_date = max_date - timedelta(days=180)
        elif date_option == "Past Year":
            start_date = max_date - timedelta(days=365)
        elif date_option == "Past 2 Years":
            start_date = max_date - timedelta(days=730)
        else:  # All Time
            start_date = min_date
        
        # Ensure start date is not before min_date
        start_date = max(start_date, min_date)
        
        date_range = (start_date, max_date)
        
        # Display the calculated range with more detail
        days_selected = (max_date - start_date).days
        st.sidebar.success(f"📅 Selected: {start_date} to {max_date} ({days_selected} days)")
    
    # Vehicle category filter
    # Determine the correct category column name
    category_col_name = 'vehicle_category' if 'vehicle_category' in processor.processed_data.columns else 'category'
    categories = processor.processed_data[category_col_name].unique()
    selected_categories = st.sidebar.multiselect(
        "Vehicle Categories",
        options=categories,
        default=categories
    )
    
    # Manufacturer filter
    manufacturers = processor.processed_data['manufacturer'].unique()
    selected_manufacturers = st.sidebar.multiselect(
        "Manufacturers",
        options=sorted(manufacturers),
        default=sorted(manufacturers)
    )
    
    # Apply filters
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = processor.filter_data(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            vehicle_categories=selected_categories,
            manufacturers=selected_manufacturers
        )
    else:
        filtered_data = processor.filter_data(
            vehicle_categories=selected_categories,
            manufacturers=selected_manufacturers
        )
    
    if filtered_data.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # Update processor with filtered data
    filtered_processor = VehicleDataProcessor(filtered_data)
    
    # Key Performance Indicators
    st.header("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_registrations = filtered_data['registrations'].sum()
        st.metric(
            "Total Registrations",
            f"{total_registrations:,}",
            help="Total vehicle registrations in selected period"
        )
    
    with col2:
        avg_monthly = filtered_data.groupby('year_month')['registrations'].sum().mean()
        st.metric(
            "Avg Monthly Registrations",
            f"{avg_monthly:,.0f}",
            help="Average registrations per month"
        )
    
    with col3:
        active_manufacturers = filtered_data['manufacturer'].nunique()
        st.metric(
            "Active Manufacturers",
            f"{active_manufacturers}",
            help="Number of manufacturers with registrations"
        )
    
    with col4:
        latest_month = filtered_data['year_month'].max()
        latest_registrations = filtered_data[
            filtered_data['year_month'] == latest_month
        ]['registrations'].sum()
        st.metric(
            "Latest Month",
            f"{latest_registrations:,}",
            help=f"Registrations in {latest_month}"
        )
    
    # Growth Metrics Section
    st.header("📊 Growth Analysis")
    
    # Calculate date range for better messaging
    if len(date_range) == 2:
        selected_days = (date_range[1] - date_range[0]).days
    else:
        selected_days = (max_date - min_date).days
    
    # YoY and QoQ tabs
    growth_tab1, growth_tab2 = st.tabs(["Year-over-Year Growth", "Quarter-over-Quarter Growth"])
    
    with growth_tab1:
        yoy_data = filtered_processor.calculate_yoy_growth()
        if not yoy_data.empty:
            # Latest year YoY growth
            latest_year = yoy_data['year'].max()
            latest_yoy = yoy_data[yoy_data['year'] == latest_year]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top growing manufacturers
                top_growth = latest_yoy.nlargest(5, 'yoy_growth_pct')[
                    ['manufacturer', category_col_name, 'yoy_growth_pct']
                ].copy()
                top_growth['yoy_growth_pct'] = top_growth['yoy_growth_pct'].round(2)
                
                st.subheader("🚀 Top Growing Manufacturers (YoY)")
                st.dataframe(top_growth, hide_index=True)
            
            with col2:
                # YoY growth chart
                fig_yoy = create_growth_chart(yoy_data, 'yoy_growth_pct', 'Year-over-Year Growth')
                st.plotly_chart(fig_yoy, use_container_width=True)
        else:
            if selected_days < 365:
                st.info(f"📅 YoY Growth requires at least 1 year of data. Selected range: {selected_days} days. Try selecting 'Past Year' or 'All Time' for growth analysis.")
            else:
                st.info("Insufficient data for YoY growth calculation. Need data from multiple years.")
    
    with growth_tab2:
        qoq_data = filtered_processor.calculate_qoq_growth()
        if not qoq_data.empty:
            # Latest quarter QoQ growth
            latest_quarter_id = qoq_data['quarter_id'].max()
            latest_qoq = qoq_data[qoq_data['quarter_id'] == latest_quarter_id]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top growing manufacturers
                top_growth_qoq = latest_qoq.nlargest(5, 'qoq_growth_pct')[
                    ['manufacturer', category_col_name, 'qoq_growth_pct']
                ].copy()
                top_growth_qoq['qoq_growth_pct'] = top_growth_qoq['qoq_growth_pct'].round(2)
                
                st.subheader("🚀 Top Growing Manufacturers (QoQ)")
                st.dataframe(top_growth_qoq, hide_index=True)
            
            with col2:
                # QoQ growth chart
                fig_qoq = create_growth_chart(qoq_data, 'qoq_growth_pct', 'Quarter-over-Quarter Growth')
                st.plotly_chart(fig_qoq, use_container_width=True)
        else:
            if selected_days < 90:
                st.info(f"📅 QoQ Growth requires at least 3 months of data. Selected range: {selected_days} days. Try selecting 'Past 3 Months' or longer for growth analysis.")
            else:
                st.info("Insufficient data for QoQ growth calculation. Need data from multiple quarters.")
    
    # Trend Analysis
    st.header("📈 Trend Analysis")
    # Determine the correct category column name
    category_col = 'vehicle_category' if 'vehicle_category' in filtered_data.columns else 'category'
    
    trend_tab1, trend_tab2, trend_tab3 = st.tabs(
        ["Registration Trends", "Market Share", "Category Comparison"]
    )
    
    with trend_tab1:
        st.subheader("Vehicle Registration Trends Over Time")
        
        # Check if we have the required columns
        if category_col not in filtered_data.columns:
            st.error(f"❌ Required column '{category_col}' not found in data. Available columns: {list(filtered_data.columns)}")
            return
        
        # Show period-specific insights
        if selected_days <= 30:
            st.info("📊 Showing daily trends for the selected period")
            # For short periods, show daily trends
            try:
                trend_data = filtered_data.groupby(['date', category_col]).agg({
                    'registrations': 'sum'
                }).reset_index()
                x_col = 'date'
                time_format = "Daily"
            except Exception as e:
                st.error(f"Error creating daily trend data: {e}")
                return
        else:
            # Trend granularity selection
            trend_granularity = st.selectbox(
                "Select Time Granularity",
                ["Monthly", "Quarterly", "Yearly"],
                index=0
            )
            time_format = trend_granularity
            
            # Create trend chart
            try:
                if trend_granularity == "Monthly":
                    trend_data = filtered_data.groupby(['year_month', category_col]).agg({
                        'registrations': 'sum'
                    }).reset_index()
                    x_col = 'year_month'
                elif trend_granularity == "Quarterly":
                    trend_data = filtered_data.groupby(['year_quarter', category_col]).agg({
                        'registrations': 'sum'
                    }).reset_index()
                    x_col = 'year_quarter'
                else:  # Yearly
                    trend_data = filtered_data.groupby(['year', category_col]).agg({
                        'registrations': 'sum'
                    }).reset_index()
                    x_col = 'year'
            except Exception as e:
                st.error(f"Error creating {trend_granularity.lower()} trend data: {e}")
                return
        
        if not trend_data.empty:
            try:
                fig_trend = create_trend_chart(trend_data, x_col, 'registrations', category_col)
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Show summary statistics for the period
                col1, col2, col3 = st.columns(3)
                with col1:
                    peak_day = trend_data.groupby(x_col)['registrations'].sum().idxmax()
                    peak_registrations = trend_data.groupby(x_col)['registrations'].sum().max()
                    st.metric("Peak Period", str(peak_day), f"{peak_registrations:,} registrations")
                
                with col2:
                    avg_period = trend_data.groupby(x_col)['registrations'].sum().mean()
                    st.metric(f"Avg {time_format}", f"{avg_period:,.0f}")
                
                with col3:
                    total_periods = trend_data[x_col].nunique()
                    st.metric(f"Total {time_format} Periods", total_periods)
            except Exception as e:
                st.error(f"Error creating trend chart: {e}")
        else:
            st.warning("No trend data available for the selected period and filters.")
    
    with trend_tab2:
        st.subheader("Market Share Analysis")
        
        # Always calculate market share for the selected period
        st.info("📊 Showing market share for the selected period")
        
        try:
            # Calculate market share for the entire selected period
            period_market_share = filtered_data.groupby(['manufacturer', category_col]).agg({
                'registrations': 'sum'
            }).reset_index()
            
            # Calculate total registrations by category for percentage calculation
            category_totals = period_market_share.groupby(category_col)['registrations'].sum().reset_index()
            category_totals = category_totals.rename(columns={'registrations': 'category_total'})
            
            # Merge to get category totals
            period_market_share = period_market_share.merge(category_totals, on=category_col)
            
            # Calculate market share percentages within each category
            period_market_share['market_share_pct'] = (
                period_market_share['registrations'] / period_market_share['category_total'] * 100
            )
            
            # Create a unique key based on the current date selection and filters
            filter_key = f"{date_range}_{sorted(selected_categories)}_{len(selected_manufacturers)}"
            
            # Market share by category
            category_choice = st.selectbox(
                "Select Vehicle Category for Market Share",
                options=period_market_share[category_col].unique(),
                key=f"market_share_category_{filter_key}"
            )
            
            # Filter for selected category
            category_market_share = period_market_share[
                period_market_share[category_col] == category_choice
            ][['manufacturer', 'registrations', 'market_share_pct']].sort_values('market_share_pct', ascending=False)
            
            if not category_market_share.empty:
                # Create pie chart
                fig_market = create_market_share_chart(
                    category_market_share, 
                    'manufacturer', 
                    'market_share_pct',
                    title=f"Market Share - {category_choice}"
                )
                st.plotly_chart(fig_market, use_container_width=True)
                
                # Show market share table
                st.dataframe(
                    category_market_share.style.format({
                        'registrations': '{:,.0f}',
                        'market_share_pct': '{:.1f}%'
                    }),
                    use_container_width=True
                )
            else:
                st.warning(f"No market share data available for {category_choice}")
                
        except Exception as e:
            st.error(f"Error creating market share analysis: {e}")
    
    with trend_tab3:
        st.subheader("Category Comparison")
        
        try:
            # Show comparison metrics for all categories in the selected period
            comparison_data = filtered_data.groupby(category_col).agg({
                'registrations': ['sum', 'mean', 'count']
            }).round(2)
            
            comparison_data.columns = ['Total Registrations', 'Average Daily', 'Days with Data']
            comparison_data = comparison_data.reset_index()
            
            if not comparison_data.empty:
                # Create comparison chart
                fig_comparison = create_category_comparison_chart(
                    comparison_data, 
                    category_col, 
                    'Total Registrations'
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # Display comparison table
                st.dataframe(
                    comparison_data.style.format({
                        'Total Registrations': '{:,.0f}',
                        'Average Daily': '{:,.0f}',
                        'Days with Data': '{:.0f}'
                    }),
                    use_container_width=True
                )
                
                # Show insights
                top_category = comparison_data.loc[comparison_data['Total Registrations'].idxmax()]
                st.success(f"🏆 **Top Performing Category:** {top_category[category_col]} with {top_category['Total Registrations']:,.0f} total registrations")
            else:
                st.warning("No category comparison data available for the selected period")
                
        except Exception as e:
            st.error(f"Error creating category comparison: {e}")

    # Category Performance Insights
    st.header("📊 Category Performance Insights")
    
    try:
        if not filtered_data.empty:
            # Show category-wise insights for the selected period
            category_summary = filtered_data.groupby(category_col).agg({
                'registrations': ['sum', 'mean', 'max', 'count']
            }).round(2)
            
            category_summary.columns = ['Total', 'Avg Daily', 'Peak Day', 'Days Active']
            category_summary = category_summary.reset_index()
            category_summary = category_summary.sort_values('Total', ascending=False)
            
            # Top performing category
            if not category_summary.empty:
                top_category = category_summary.iloc[0]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Top Category",
                        top_category[category_col],
                        f"{top_category['Total']:,.0f} registrations"
                    )
                
                with col2:
                    avg_per_category = category_summary['Total'].mean()
                    st.metric("Avg per Category", f"{avg_per_category:,.0f}")
                
                with col3:
                    active_categories = len(category_summary)
                    st.metric("Active Categories", active_categories)
                
                # Show category breakdown
                st.subheader("Category Performance Breakdown")
                st.dataframe(
                    category_summary.style.format({
                        'Total': '{:,.0f}',
                        'Avg Daily': '{:,.0f}',
                        'Peak Day': '{:,.0f}',
                        'Days Active': '{:.0f}'
                    }),
                    use_container_width=True
                )
        else:
            st.warning("No category trend data available for the selected period.")
    except Exception as e:
        st.error(f"Error in category insights: {e}")
    
    # Data Export Section
    st.header("💾 Data Export")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📥 Download Filtered Data (CSV)"):
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"vehicle_registrations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with export_col2:
        if st.button("📊 Download Growth Analysis (CSV)"):
            yoy_data = filtered_processor.calculate_yoy_growth()
            if not yoy_data.empty:
                csv = yoy_data.to_csv(index=False)
                st.download_button(
                    label="Download Growth Data",
                    data=csv,
                    file_name=f"growth_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>Vehicle Registration Dashboard | Data Source: Vahan Portal | 
        Built with Streamlit & Plotly</p>
        <p><em>Note: This dashboard uses sample data for demonstration purposes.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
