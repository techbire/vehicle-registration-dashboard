"""
Growth Calculations Module

This module contains utility functions for calculating various growth metrics
including YoY, QoQ, MoM, CAGR, and other statistical measures.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GrowthCalculator:
    """
    Calculate various growth metrics for time series data.
    """
    
    @staticmethod
    def calculate_yoy_growth(data: pd.DataFrame, 
                           value_col: str = 'registrations',
                           group_cols: List[str] = None,
                           date_col: str = 'date') -> pd.DataFrame:
        """
        Calculate Year-over-Year growth rates.
        
        Args:
            data: DataFrame containing time series data
            value_col: Column name containing values to calculate growth for
            group_cols: List of columns to group by (e.g., manufacturer, category)
            date_col: Column name containing date information
            
        Returns:
            DataFrame with YoY growth calculations
        """
        if group_cols is None:
            group_cols = []
        
        df = data.copy()
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        df['year'] = df[date_col].dt.year
        
        # Group by year and other specified columns
        group_cols_with_year = ['year'] + group_cols
        
        # Aggregate by year
        yearly_data = df.groupby(group_cols_with_year)[value_col].sum().reset_index()
        
        # Sort for proper shift operation
        sort_cols = group_cols + ['year'] if group_cols else ['year']
        yearly_data = yearly_data.sort_values(sort_cols)
        
        # Calculate YoY growth
        if group_cols:
            yearly_data['prev_year_value'] = yearly_data.groupby(group_cols)[value_col].shift(1)
        else:
            yearly_data['prev_year_value'] = yearly_data[value_col].shift(1)
        
        yearly_data['yoy_growth_abs'] = yearly_data[value_col] - yearly_data['prev_year_value']
        yearly_data['yoy_growth_pct'] = (
            yearly_data['yoy_growth_abs'] / yearly_data['prev_year_value'] * 100
        )
        
        # Handle edge cases
        yearly_data['yoy_growth_pct'] = yearly_data['yoy_growth_pct'].replace([np.inf, -np.inf], np.nan)
        
        return yearly_data
    
    @staticmethod
    def calculate_qoq_growth(data: pd.DataFrame,
                           value_col: str = 'registrations',
                           group_cols: List[str] = None,
                           date_col: str = 'date') -> pd.DataFrame:
        """
        Calculate Quarter-over-Quarter growth rates.
        
        Args:
            data: DataFrame containing time series data
            value_col: Column name containing values to calculate growth for
            group_cols: List of columns to group by
            date_col: Column name containing date information
            
        Returns:
            DataFrame with QoQ growth calculations
        """
        if group_cols is None:
            group_cols = []
        
        df = data.copy()
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        df['year'] = df[date_col].dt.year
        df['quarter'] = df[date_col].dt.quarter
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        
        # Create sortable quarter identifier
        df['quarter_id'] = df['year'] * 10 + df['quarter']
        
        # Group by quarter and other specified columns
        group_cols_with_quarter = ['year', 'quarter', 'quarter_id'] + group_cols
        
        # Aggregate by quarter
        quarterly_data = df.groupby(group_cols_with_quarter)[value_col].sum().reset_index()
        
        # Sort for proper shift operation
        sort_cols = group_cols + ['quarter_id'] if group_cols else ['quarter_id']
        quarterly_data = quarterly_data.sort_values(sort_cols)
        
        # Calculate QoQ growth
        if group_cols:
            quarterly_data['prev_quarter_value'] = quarterly_data.groupby(group_cols)[value_col].shift(1)
        else:
            quarterly_data['prev_quarter_value'] = quarterly_data[value_col].shift(1)
        
        quarterly_data['qoq_growth_abs'] = quarterly_data[value_col] - quarterly_data['prev_quarter_value']
        quarterly_data['qoq_growth_pct'] = (
            quarterly_data['qoq_growth_abs'] / quarterly_data['prev_quarter_value'] * 100
        )
        
        # Handle edge cases
        quarterly_data['qoq_growth_pct'] = quarterly_data['qoq_growth_pct'].replace([np.inf, -np.inf], np.nan)
        
        return quarterly_data
    
    @staticmethod
    def calculate_mom_growth(data: pd.DataFrame,
                           value_col: str = 'registrations',
                           group_cols: List[str] = None,
                           date_col: str = 'date') -> pd.DataFrame:
        """
        Calculate Month-over-Month growth rates.
        
        Args:
            data: DataFrame containing time series data
            value_col: Column name containing values to calculate growth for
            group_cols: List of columns to group by
            date_col: Column name containing date information
            
        Returns:
            DataFrame with MoM growth calculations
        """
        if group_cols is None:
            group_cols = []
        
        df = data.copy()
        
        # Ensure date column is datetime
        df[date_col] = pd.to_datetime(df[date_col])
        df['year_month'] = df[date_col].dt.strftime('%Y-%m')
        
        # Group by month and other specified columns
        group_cols_with_month = ['year_month'] + group_cols
        
        # Aggregate by month
        monthly_data = df.groupby(group_cols_with_month)[value_col].sum().reset_index()
        
        # Sort for proper shift operation
        sort_cols = group_cols + ['year_month'] if group_cols else ['year_month']
        monthly_data = monthly_data.sort_values(sort_cols)
        
        # Calculate MoM growth
        if group_cols:
            monthly_data['prev_month_value'] = monthly_data.groupby(group_cols)[value_col].shift(1)
        else:
            monthly_data['prev_month_value'] = monthly_data[value_col].shift(1)
        
        monthly_data['mom_growth_abs'] = monthly_data[value_col] - monthly_data['prev_month_value']
        monthly_data['mom_growth_pct'] = (
            monthly_data['mom_growth_abs'] / monthly_data['prev_month_value'] * 100
        )
        
        # Handle edge cases
        monthly_data['mom_growth_pct'] = monthly_data['mom_growth_pct'].replace([np.inf, -np.inf], np.nan)
        
        return monthly_data
    
    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, periods: float) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR).
        
        Args:
            start_value: Starting value
            end_value: Ending value
            periods: Number of periods (usually years)
            
        Returns:
            CAGR as a percentage
        """
        if start_value <= 0 or end_value <= 0 or periods <= 0:
            return np.nan
        
        cagr = (pow(end_value / start_value, 1 / periods) - 1) * 100
        return cagr
    
    @staticmethod
    def calculate_moving_average(data: pd.Series, window: int = 3) -> pd.Series:
        """
        Calculate moving average for smoothing trends.
        
        Args:
            data: Series containing values
            window: Window size for moving average
            
        Returns:
            Series with moving average values
        """
        return data.rolling(window=window, center=True).mean()
    
    @staticmethod
    def calculate_growth_acceleration(growth_rates: pd.Series) -> pd.Series:
        """
        Calculate growth acceleration (change in growth rate).
        
        Args:
            growth_rates: Series containing growth rates
            
        Returns:
            Series with growth acceleration values
        """
        return growth_rates.diff()
    
    @staticmethod
    def detect_trend(data: pd.Series, min_periods: int = 3) -> str:
        """
        Detect overall trend in the data.
        
        Args:
            data: Series containing values
            min_periods: Minimum periods to consider for trend detection
            
        Returns:
            Trend description: 'increasing', 'decreasing', 'stable', or 'insufficient_data'
        """
        if len(data) < min_periods:
            return 'insufficient_data'
        
        # Remove NaN values
        clean_data = data.dropna()
        
        if len(clean_data) < min_periods:
            return 'insufficient_data'
        
        # Calculate trend using linear regression slope
        x = np.arange(len(clean_data))
        y = clean_data.values
        
        # Simple linear regression
        slope = np.polyfit(x, y, 1)[0]
        
        # Define thresholds based on data magnitude
        mean_value = np.mean(y)
        threshold = abs(mean_value * 0.05)  # 5% of mean as threshold
        
        if slope > threshold:
            return 'increasing'
        elif slope < -threshold:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def calculate_volatility(data: pd.Series, window: int = 12) -> float:
        """
        Calculate volatility (standard deviation of returns).
        
        Args:
            data: Series containing values
            window: Window for calculating rolling volatility
            
        Returns:
            Volatility measure
        """
        # Calculate period-over-period returns
        returns = data.pct_change().dropna()
        
        if len(returns) < 2:
            return np.nan
        
        # Calculate rolling standard deviation
        volatility = returns.rolling(window=min(window, len(returns))).std().iloc[-1]
        
        return volatility * 100 if not pd.isna(volatility) else np.nan
    
    @staticmethod
    def calculate_market_share(data: pd.DataFrame,
                             value_col: str = 'registrations',
                             category_col: str = 'vehicle_category',
                             entity_col: str = 'manufacturer',
                             period_col: str = 'year') -> pd.DataFrame:
        """
        Calculate market share for entities within categories and periods.
        
        Args:
            data: DataFrame containing the data
            value_col: Column containing values to calculate share for
            category_col: Column defining market categories
            entity_col: Column defining entities (e.g., manufacturers)
            period_col: Column defining time periods
            
        Returns:
            DataFrame with market share calculations
        """
        df = data.copy()
        
        # Group by period, category, and entity
        grouped = df.groupby([period_col, category_col, entity_col])[value_col].sum().reset_index()
        
        # Calculate total by period and category
        totals = grouped.groupby([period_col, category_col])[value_col].sum().reset_index()
        totals = totals.rename(columns={value_col: 'total_market'})
        
        # Merge with grouped data
        market_share_data = grouped.merge(totals, on=[period_col, category_col])
        
        # Calculate market share percentage
        market_share_data['market_share_pct'] = (
            market_share_data[value_col] / market_share_data['total_market'] * 100
        )
        
        return market_share_data
    
    @staticmethod
    def calculate_growth_consistency(growth_rates: pd.Series) -> Dict[str, float]:
        """
        Calculate metrics to assess growth consistency.
        
        Args:
            growth_rates: Series containing growth rates
            
        Returns:
            Dictionary with consistency metrics
        """
        clean_rates = growth_rates.dropna()
        
        if len(clean_rates) < 2:
            return {
                'mean_growth': np.nan,
                'std_growth': np.nan,
                'coefficient_variation': np.nan,
                'positive_periods': np.nan,
                'consistency_score': np.nan
            }
        
        mean_growth = clean_rates.mean()
        std_growth = clean_rates.std()
        coefficient_variation = std_growth / abs(mean_growth) if mean_growth != 0 else np.inf
        
        # Percentage of positive growth periods
        positive_periods = (clean_rates > 0).sum() / len(clean_rates) * 100
        
        # Consistency score (lower coefficient of variation = higher consistency)
        consistency_score = 1 / (1 + coefficient_variation) if not np.isinf(coefficient_variation) else 0
        
        return {
            'mean_growth': mean_growth,
            'std_growth': std_growth,
            'coefficient_variation': coefficient_variation,
            'positive_periods': positive_periods,
            'consistency_score': consistency_score
        }


# Utility functions for advanced calculations
def calculate_seasonal_indices(data: pd.DataFrame,
                             value_col: str = 'registrations',
                             date_col: str = 'date') -> pd.DataFrame:
    """
    Calculate seasonal indices for identifying seasonal patterns.
    
    Args:
        data: DataFrame containing time series data
        value_col: Column containing values
        date_col: Column containing dates
        
    Returns:
        DataFrame with seasonal indices
    """
    df = data.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['month'] = df[date_col].dt.month
    df['year'] = df[date_col].dt.year
    
    # Calculate monthly averages by year
    monthly_data = df.groupby(['year', 'month'])[value_col].sum().reset_index()
    
    # Calculate overall monthly averages
    monthly_avg = monthly_data.groupby('month')[value_col].mean()
    
    # Calculate seasonal indices (month average / overall average)
    overall_avg = monthly_avg.mean()
    seasonal_indices = (monthly_avg / overall_avg).reset_index()
    seasonal_indices.columns = ['month', 'seasonal_index']
    
    return seasonal_indices


def calculate_growth_benchmarks(data: pd.DataFrame,
                              growth_col: str = 'yoy_growth_pct',
                              entity_col: str = 'manufacturer') -> Dict[str, float]:
    """
    Calculate growth benchmarks for comparison purposes.
    
    Args:
        data: DataFrame containing growth data
        growth_col: Column containing growth rates
        entity_col: Column defining entities
        
    Returns:
        Dictionary with benchmark metrics
    """
    clean_data = data[data[growth_col].notna()]
    
    if clean_data.empty:
        return {}
    
    growth_rates = clean_data[growth_col]
    
    benchmarks = {
        'p25': np.percentile(growth_rates, 25),
        'median': np.percentile(growth_rates, 50),
        'p75': np.percentile(growth_rates, 75),
        'p90': np.percentile(growth_rates, 90),
        'mean': growth_rates.mean(),
        'std': growth_rates.std(),
        'min': growth_rates.min(),
        'max': growth_rates.max()
    }
    
    return benchmarks


# Example usage and testing
def main():
    """Test the growth calculation functions."""
    # Create sample data
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='M')
    np.random.seed(42)
    
    sample_data = []
    for date in dates:
        for category in ['2W', '3W', '4W']:
            for manufacturer in ['Company A', 'Company B']:
                base_value = 1000 if category == '2W' else 500
                trend = (date.year - 2020) * 50
                seasonal = 100 * np.sin(2 * np.pi * date.month / 12)
                noise = np.random.normal(0, 50)
                
                registrations = max(0, base_value + trend + seasonal + noise)
                
                sample_data.append({
                    'date': date,
                    'vehicle_category': category,
                    'manufacturer': manufacturer,
                    'registrations': int(registrations)
                })
    
    df = pd.DataFrame(sample_data)
    
    # Test growth calculations
    calculator = GrowthCalculator()
    
    # YoY growth
    yoy_growth = calculator.calculate_yoy_growth(
        df, group_cols=['vehicle_category', 'manufacturer']
    )
    print("YoY Growth Sample:")
    print(yoy_growth.head())
    
    # QoQ growth
    qoq_growth = calculator.calculate_qoq_growth(
        df, group_cols=['vehicle_category', 'manufacturer']
    )
    print("\nQoQ Growth Sample:")
    print(qoq_growth.head())
    
    # Market share
    market_share = calculator.calculate_market_share(df)
    print("\nMarket Share Sample:")
    print(market_share.head())


if __name__ == "__main__":
    main()
