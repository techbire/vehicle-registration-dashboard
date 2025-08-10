# Data Directory

This directory contains the vehicle registration data used by the dashboard.

## Structure

- `raw/` - Raw data files as collected from the Vahan portal
- `processed/` - Cleaned and processed data files ready for analysis

## Data Files

The main data file `vehicle_registrations.csv` contains the following columns:
- `date` - Registration date
- `year` - Year of registration
- `quarter` - Quarter (Q1, Q2, Q3, Q4)
- `month` - Month in YYYY-MM format
- `vehicle_category` - Vehicle type (2W, 3W, 4W)
- `manufacturer` - Vehicle manufacturer name
- `registrations` - Number of registrations

## Data Sources

1. **Vahan Portal**: https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
2. **Sample Data**: Generated realistic data for demonstration purposes

## Usage

The data can be loaded using pandas:

```python
import pandas as pd

# Load raw data
df = pd.read_csv('data/raw/vehicle_registrations.csv')

# Load processed data
processed_df = pd.read_csv('data/processed/cleaned_vehicle_data.csv')
```

## Data Quality

- All registration numbers are positive integers
- Dates are in YYYY-MM-DD format
- No missing values in core columns
- Manufacturer names are standardized
- Categories are limited to 2W, 3W, 4W

## Updates

Data should be updated regularly from the Vahan portal. The scraper module handles this process automatically.
