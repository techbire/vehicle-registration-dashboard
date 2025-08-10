"""
Data Processing Module

This module handles data cleaning, transformation, and analysis
for vehicle registration data including YoY and QoQ calculations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VehicleDataProcessor:
    """
    Process and analyze vehicle registration data.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize processor with vehicle data.
        
        Args:
            data: DataFrame with vehicle registration data
        """
        self.raw_data = data.copy()
        self.processed_data = None
        self._prepare_data()
    
    def _prepare_data(self) -> None:
        """Prepare and clean the data for analysis."""
        df = self.raw_data.copy()
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Add time-based columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        
        # Ensure registrations is numeric
        df['registrations'] = pd.to_numeric(df['registrations'], errors='coerce').fillna(0)
        
        self.processed_data = df
        logger.info(f"Processed {len(df)} records")
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of the data."""
        df = self.processed_data
        
        stats = {
            'total_records': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'total_registrations': df['registrations'].sum(),
            'vehicle_categories': df['vehicle_category'].unique().tolist(),
            'manufacturers': df['manufacturer'].unique().tolist(),
            'years_covered': sorted(df['year'].unique().tolist()),
            'avg_monthly_registrations': df.groupby('year_month')['registrations'].sum().mean()
        }
        
        return stats
    
    def aggregate_by_period(self, period: str = 'month') -> pd.DataFrame:
        """
        Aggregate data by time period.
        
        Args:
            period: 'month', 'quarter', or 'year'
            
        Returns:
            Aggregated DataFrame
        """
        df = self.processed_data
        
        if period == 'month':
            group_cols = ['year_month', 'vehicle_category', 'manufacturer']
        elif period == 'quarter':
            group_cols = ['year_quarter', 'vehicle_category', 'manufacturer']
        elif period == 'year':
            group_cols = ['year', 'vehicle_category', 'manufacturer']
        else:
            raise ValueError("Period must be 'month', 'quarter', or 'year'")
        
        aggregated = df.groupby(group_cols).agg({
            'registrations': 'sum',
            'date': 'first'
        }).reset_index()
        
        return aggregated
    
    def calculate_yoy_growth(self) -> pd.DataFrame:
        """
        Calculate Year-over-Year growth rates.
        
        Returns:
            DataFrame with YoY growth calculations
        """
        df = self.processed_data
        
        # Aggregate by year, category, and manufacturer
        yearly_data = df.groupby(['year', 'vehicle_category', 'manufacturer']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Calculate YoY growth
        yearly_data = yearly_data.sort_values(['vehicle_category', 'manufacturer', 'year'])
        
        yearly_data['prev_year_registrations'] = yearly_data.groupby(
            ['vehicle_category', 'manufacturer']
        )['registrations'].shift(1)
        
        yearly_data['yoy_growth_abs'] = (
            yearly_data['registrations'] - yearly_data['prev_year_registrations']
        )
        
        yearly_data['yoy_growth_pct'] = (
            yearly_data['yoy_growth_abs'] / yearly_data['prev_year_registrations'] * 100
        )
        
        # Handle infinite and NaN values
        yearly_data['yoy_growth_pct'] = yearly_data['yoy_growth_pct'].replace([np.inf, -np.inf], np.nan)
        
        return yearly_data
    
    def calculate_qoq_growth(self) -> pd.DataFrame:
        """
        Calculate Quarter-over-Quarter growth rates.
        
        Returns:
            DataFrame with QoQ growth calculations
        """
        df = self.processed_data
        
        # Aggregate by quarter, category, and manufacturer
        quarterly_data = df.groupby(['year', 'quarter', 'vehicle_category', 'manufacturer']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Create a sortable quarter identifier
        quarterly_data['quarter_id'] = quarterly_data['year'] * 10 + quarterly_data['quarter']
        quarterly_data = quarterly_data.sort_values(['vehicle_category', 'manufacturer', 'quarter_id'])
        
        # Calculate QoQ growth
        quarterly_data['prev_quarter_registrations'] = quarterly_data.groupby(
            ['vehicle_category', 'manufacturer']
        )['registrations'].shift(1)
        
        quarterly_data['qoq_growth_abs'] = (
            quarterly_data['registrations'] - quarterly_data['prev_quarter_registrations']
        )
        
        quarterly_data['qoq_growth_pct'] = (
            quarterly_data['qoq_growth_abs'] / quarterly_data['prev_quarter_registrations'] * 100
        )
        
        # Handle infinite and NaN values
        quarterly_data['qoq_growth_pct'] = quarterly_data['qoq_growth_pct'].replace([np.inf, -np.inf], np.nan)
        
        return quarterly_data
    
    def get_category_trends(self) -> pd.DataFrame:
        """Get trends by vehicle category."""
        df = self.processed_data
        
        category_trends = df.groupby(['year_month', 'vehicle_category']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Calculate monthly growth for each category
        category_trends = category_trends.sort_values(['vehicle_category', 'year_month'])
        
        category_trends['prev_month_registrations'] = category_trends.groupby(
            'vehicle_category'
        )['registrations'].shift(1)
        
        category_trends['mom_growth_pct'] = (
            (category_trends['registrations'] - category_trends['prev_month_registrations']) /
            category_trends['prev_month_registrations'] * 100
        )
        
        return category_trends
    
    def get_manufacturer_rankings(self, period: str = 'year', top_n: int = 10) -> pd.DataFrame:
        """
        Get top manufacturers by registration volume.
        
        Args:
            period: 'month', 'quarter', or 'year'
            top_n: Number of top manufacturers to return
            
        Returns:
            DataFrame with manufacturer rankings
        """
        df = self.processed_data
        
        if period == 'year':
            group_col = 'year'
        elif period == 'quarter':
            group_col = 'year_quarter'
        elif period == 'month':
            group_col = 'year_month'
        else:
            raise ValueError("Period must be 'month', 'quarter', or 'year'")
        
        # Get latest period
        latest_period = df[group_col].max()
        
        # Filter for latest period and rank manufacturers
        latest_data = df[df[group_col] == latest_period]
        
        rankings = latest_data.groupby(['manufacturer', 'vehicle_category']).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Overall rankings
        overall_rankings = rankings.groupby('manufacturer').agg({
            'registrations': 'sum'
        }).reset_index().sort_values('registrations', ascending=False)
        
        return overall_rankings.head(top_n)
    
    def filter_data(self, 
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   vehicle_categories: Optional[List[str]] = None,
                   manufacturers: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Filter data based on criteria.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            vehicle_categories: List of vehicle categories to include
            manufacturers: List of manufacturers to include
            
        Returns:
            Filtered DataFrame
        """
        df = self.processed_data.copy()
        
        # Date filtering
        if start_date:
            df = df[df['date'] >= pd.to_datetime(start_date)]
        
        if end_date:
            df = df[df['date'] <= pd.to_datetime(end_date)]
        
        # Category filtering
        if vehicle_categories:
            df = df[df['vehicle_category'].isin(vehicle_categories)]
        
        # Manufacturer filtering
        if manufacturers:
            df = df[df['manufacturer'].isin(manufacturers)]
        
        return df
    
    def get_market_share(self, period: str = 'year') -> pd.DataFrame:
        """
        Calculate market share by manufacturer and category.
        
        Args:
            period: 'month', 'quarter', or 'year'
            
        Returns:
            DataFrame with market share calculations
        """
        df = self.processed_data
        
        if period == 'year':
            group_cols = ['year', 'vehicle_category', 'manufacturer']
        elif period == 'quarter':
            group_cols = ['year_quarter', 'vehicle_category', 'manufacturer']
        elif period == 'month':
            group_cols = ['year_month', 'vehicle_category', 'manufacturer']
        else:
            raise ValueError("Period must be 'month', 'quarter', or 'year'")
        
        # Aggregate data
        market_data = df.groupby(group_cols).agg({
            'registrations': 'sum'
        }).reset_index()
        
        # Calculate total registrations per period and category
        period_col = group_cols[0]
        category_totals = market_data.groupby([period_col, 'vehicle_category']).agg({
            'registrations': 'sum'
        }).rename(columns={'registrations': 'category_total'}).reset_index()
        
        # Merge and calculate market share
        market_share = market_data.merge(
            category_totals, 
            on=[period_col, 'vehicle_category']
        )
        
        market_share['market_share_pct'] = (
            market_share['registrations'] / market_share['category_total'] * 100
        )
        
        return market_share


def main():
    """Test the data processor with sample data."""
    from .scraper import VahanDataScraper
    
    # Load sample data
    scraper = VahanDataScraper()
    df = scraper.load_sample_data()
    
    # Process data
    processor = VehicleDataProcessor(df)
    
    # Display summary
    stats = processor.get_summary_stats()
    print("Data Summary:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Calculate growth metrics
    print("\nCalculating growth metrics...")
    yoy_growth = processor.calculate_yoy_growth()
    qoq_growth = processor.calculate_qoq_growth()
    
    print(f"YoY Growth calculations: {len(yoy_growth)} records")
    print(f"QoQ Growth calculations: {len(qoq_growth)} records")
    
    # Show top manufacturers
    top_manufacturers = processor.get_manufacturer_rankings()
    print("\nTop Manufacturers (Latest Year):")
    print(top_manufacturers.to_string(index=False))


if __name__ == "__main__":
    main()
