"""
Vehicle Registration Data Scraper

This module handles data collection from the Vahan portal.
Since the Vahan portal requires interactive elements and may have
anti-scraping measures, this module provides a framework for
data collection and includes sample data generation for demonstration.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VahanDataScraper:
    """
    Scraper for Vahan portal vehicle registration data.
    
    Note: The actual Vahan portal may require JavaScript rendering
    and might have CAPTCHA protection. This implementation provides
    a framework and generates realistic sample data for demonstration.
    """
    
    def __init__(self):
        self.base_url = "https://vahan.parivahan.gov.in/vahan4dashboard/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_vehicle_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Scrape vehicle registration data from Vahan portal.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame containing vehicle registration data
        """
        try:
            # Attempt to scrape real data
            data = self._scrape_real_data(start_date, end_date)
            if data is not None:
                return data
        except Exception as e:
            logger.warning(f"Real data scraping failed: {e}")
            
        # Fallback to sample data generation
        logger.info("Generating sample data for demonstration...")
        return self._generate_sample_data(start_date, end_date)
    
    def _scrape_real_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Attempt to scrape real data from Vahan portal.
        
        Note: This is a template. The actual implementation would need
        to handle JavaScript rendering, form submissions, and potential
        CAPTCHA challenges.
        """
        try:
            # This is a simplified approach - real implementation would need
            # Selenium or similar tools for JavaScript-heavy sites
            response = self.session.get(f"{self.base_url}vahan/view/reportview.xhtml")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse the page structure and extract data
                # This would require detailed analysis of the portal's structure
                logger.info("Successfully accessed Vahan portal")
                # Return None for now as real scraping needs more complex setup
                return None
            else:
                logger.error(f"Failed to access portal: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping real data: {e}")
            return None
    
    def _generate_sample_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate realistic sample data for demonstration purposes.
        """
        # Define vehicle categories and manufacturers
        vehicle_categories = ['2W', '3W', '4W']
        manufacturers = {
            '2W': ['Hero MotoCorp', 'Honda', 'TVS', 'Bajaj', 'Yamaha', 'Royal Enfield'],
            '3W': ['Bajaj', 'Mahindra', 'Piaggio', 'Force Motors', 'Atul Auto'],
            '4W': ['Maruti Suzuki', 'Hyundai', 'Tata Motors', 'Mahindra', 'Kia', 'Honda Cars']
        }
        
        # Generate date range
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        data = []
        current_date = start
        
        while current_date <= end:
            for category in vehicle_categories:
                for manufacturer in manufacturers[category]:
                    # Generate realistic registration numbers with trends
                    base_registrations = self._get_base_registrations(category, manufacturer)
                    seasonal_factor = self._get_seasonal_factor(current_date)
                    growth_factor = self._get_growth_factor(current_date, category)
                    
                    registrations = int(base_registrations * seasonal_factor * growth_factor)
                    registrations += random.randint(-100, 100)  # Add some randomness
                    registrations = max(0, registrations)  # Ensure non-negative
                    
                    data.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'year': current_date.year,
                        'quarter': f"Q{((current_date.month - 1) // 3) + 1}",
                        'month': current_date.strftime('%Y-%m'),
                        'vehicle_category': category,
                        'manufacturer': manufacturer,
                        'registrations': registrations
                    })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        logger.info(f"Generated {len(df)} sample records")
        return df
    
    def _get_base_registrations(self, category: str, manufacturer: str) -> int:
        """Get base registration numbers for category and manufacturer."""
        base_values = {
            '2W': {'Hero MotoCorp': 50000, 'Honda': 35000, 'TVS': 25000, 
                   'Bajaj': 20000, 'Yamaha': 15000, 'Royal Enfield': 8000},
            '3W': {'Bajaj': 8000, 'Mahindra': 6000, 'Piaggio': 4000, 
                   'Force Motors': 2000, 'Atul Auto': 1500},
            '4W': {'Maruti Suzuki': 45000, 'Hyundai': 25000, 'Tata Motors': 20000, 
                   'Mahindra': 15000, 'Kia': 12000, 'Honda Cars': 10000}
        }
        return base_values.get(category, {}).get(manufacturer, 1000)
    
    def _get_seasonal_factor(self, date: datetime) -> float:
        """Get seasonal factor based on month."""
        # Festival seasons typically see higher vehicle sales
        seasonal_factors = {
            1: 0.8,   # January
            2: 0.85,  # February
            3: 0.9,   # March
            4: 1.1,   # April (New year)
            5: 1.0,   # May
            6: 0.9,   # June
            7: 0.95,  # July
            8: 1.1,   # August (Monsoon end)
            9: 1.2,   # September (Festival season)
            10: 1.3,  # October (Peak festival)
            11: 1.15, # November (Post festival)
            12: 0.95  # December
        }
        return seasonal_factors.get(date.month, 1.0)
    
    def _get_growth_factor(self, date: datetime, category: str) -> float:
        """Get growth factor based on year and vehicle category."""
        base_year = 2020
        years_passed = date.year - base_year
        
        # Different growth rates for different categories
        annual_growth_rates = {
            '2W': 0.05,  # 5% annual growth
            '3W': 0.08,  # 8% annual growth  
            '4W': 0.12   # 12% annual growth
        }
        
        growth_rate = annual_growth_rates.get(category, 0.07)
        return (1 + growth_rate) ** years_passed
    
    def save_data(self, df: pd.DataFrame, filename: str) -> None:
        """Save scraped data to file."""
        data_dir = Path("data/raw")
        data_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = data_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Data saved to {filepath}")
    
    def load_sample_data(self) -> pd.DataFrame:
        """Load or generate sample data for the dashboard."""
        # Generate data for the last 3 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)
        
        return self.scrape_vehicle_data(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )


def main():
    """Main function to run data scraping."""
    scraper = VahanDataScraper()
    
    # Generate sample data for demonstration
    print("Generating vehicle registration data...")
    df = scraper.load_sample_data()
    
    # Save the data
    scraper.save_data(df, "vehicle_registrations.csv")
    
    # Display summary
    print(f"\nData Summary:")
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Vehicle categories: {df['vehicle_category'].unique()}")
    print(f"Total manufacturers: {df['manufacturer'].nunique()}")
    
    print("\nSample data generated successfully!")
    print("Note: This is demonstration data. For production use, implement")
    print("proper web scraping with tools like Selenium for JavaScript-heavy sites.")


if __name__ == "__main__":
    main()
