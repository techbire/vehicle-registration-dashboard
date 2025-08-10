# Vehicle Registration Dashboard

A comprehensive interactive dashboard for analyzing vehicle registration data from the Vahan portal, designed for investor insights.

## Features

- **Data Visualization**: Interactive charts and graphs for vehicle registration trends
- **Growth Analysis**: Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) growth metrics
- **Filtering**: Filter by vehicle categories (2W/3W/4W) and manufacturers
- **Date Range Selection**: Analyze data across custom time periods
- **Investor-Friendly UI**: Clean, professional interface built with Streamlit

## Data Source

This dashboard uses public data from the [Vahan Dashboard](https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml) focusing on:
- Vehicle type-wise data (2-Wheeler, 3-Wheeler, 4-Wheeler)
- Manufacturer-wise registration data

## Project Structure

```
vehicle-registration-dashboard/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Data collection from Vahan portal
│   │   └── processor.py        # Data processing and analysis
│   ├── dashboard/
│   │   ├── __init__.py
│   │   ├── app.py             # Main Streamlit application
│   │   ├── components.py      # UI components
│   │   └── charts.py          # Chart generation
│   └── utils/
│       ├── __init__.py
│       ├── database.py        # Database operations
│       └── calculations.py    # Growth calculations
├── data/
│   ├── raw/                   # Raw scraped data
│   └── processed/             # Cleaned and processed data
├── tests/
├── requirements.txt
├── setup.py
└── README.md
```

## Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run data collection (if needed):
   ```bash
   python -m src.data.scraper
   ```

2. Launch the dashboard:
   ```bash
   streamlit run src/dashboard/app.py
   ```

3. Open your browser to `http://localhost:8501`

## Technical Stack

- **Python 3.8+**: Core programming language
- **Streamlit**: Web dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and visualizations
- **Requests/BeautifulSoup**: Web scraping
- **SQLite**: Local database for data storage

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
This project follows PEP 8 guidelines. Run linting with:
```bash
flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project uses publicly available data from the Vahan portal for educational and analytical purposes. Please ensure compliance with the portal's terms of service when using this tool.
