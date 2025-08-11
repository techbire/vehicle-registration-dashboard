"""
Quick test to verify trend analysis functionality
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from src.data.scraper import VahanDataScraper
from src.data.processor import VehicleDataProcessor
import pandas as pd

def test_trend_analysis():
    """Test trend analysis components"""
    print("🔍 Testing Trend Analysis Components...")
    
    # Generate sample data
    scraper = VahanDataScraper()
    print("📊 Generating sample data...")
    sample_data = scraper.generate_sample_data()
    print(f"✅ Generated {len(sample_data)} records")
    
    # Initialize processor
    processor = VehicleDataProcessor(sample_data)
    print("🔧 Initialized data processor")
    
    # Check column names
    print("📋 Checking column names:")
    print(f"   Columns: {list(processor.processed_data.columns)}")
    
    category_col = 'vehicle_category' if 'vehicle_category' in processor.processed_data.columns else 'category'
    print(f"   Category column: {category_col}")
    print(f"   Categories: {processor.processed_data[category_col].unique().tolist()}")
    
    # Test trend data creation
    print("\n📈 Testing trend data creation...")
    try:
        # Daily trends
        daily_trends = processor.processed_data.groupby(['date', category_col]).agg({
            'registrations': 'sum'
        }).reset_index()
        print(f"✅ Daily trends: {len(daily_trends)} records")
        
        # Monthly trends
        monthly_trends = processor.processed_data.groupby(['year_month', category_col]).agg({
            'registrations': 'sum'
        }).reset_index()
        print(f"✅ Monthly trends: {len(monthly_trends)} records")
        
        # Sample data
        print("\n📋 Sample daily trend data:")
        print(daily_trends.head())
        
        print("\n📋 Sample monthly trend data:")
        print(monthly_trends.head())
        
        print("\n🎉 All trend analysis components working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in trend analysis: {e}")
        return False

if __name__ == "__main__":
    test_trend_analysis()
