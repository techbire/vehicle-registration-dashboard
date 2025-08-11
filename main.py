"""
Main entry point for the Vehicle Registration Dashboard application.

This script provides a command-line interface for running different
components of the dashboard system.
"""

import argparse
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.data.scraper import VahanDataScraper
from src.data.processor import VehicleDataProcessor
from src.utils.database import DatabaseManager


def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dashboard.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_data_collection():
    """Run data collection from Vahan portal."""
    print("Starting data collection...")
    
    scraper = VahanDataScraper()
    data = scraper.load_sample_data()
    
    # Save data
    scraper.save_data(data, 'vehicle_registrations.csv')
    
    # Store in database
    db_manager = DatabaseManager()
    db_manager.insert_vehicle_data(data)
    
    print(f"Collected {len(data)} records successfully!")
    return True


def run_data_processing():
    """Run data processing and analysis."""
    print("Starting data processing...")
    
    # Load data from database
    db_manager = DatabaseManager()
    data = db_manager.get_vehicle_data()
    
    if data.empty:
        print("No data found in database. Run data collection first.")
        return False
    
    # Process data
    processor = VehicleDataProcessor(data)
    
    # Calculate growth metrics
    yoy_growth = processor.calculate_yoy_growth()
    qoq_growth = processor.calculate_qoq_growth()
    
    # Store growth metrics
    if not yoy_growth.empty:
        db_manager.store_growth_metrics(yoy_growth, 'yearly')
    
    if not qoq_growth.empty:
        db_manager.store_growth_metrics(qoq_growth, 'quarterly')
    
    print("Data processing completed successfully!")
    return True


def run_dashboard():
    """Launch the Streamlit dashboard."""
    print("Launching dashboard...")
    
    import os
    
    # Change to the current directory
    os.chdir(Path(__file__).parent)
    
    # Always run the app directly in deployment mode
    print("Running dashboard directly")
    try:
        from src.dashboard.app import main as dashboard_main
        dashboard_main()
        return True
    except Exception as e:
        print(f"Error running dashboard directly: {e}")
        # If direct import fails, try alternative approach
        try:
            import subprocess
            # For local development only
            if not os.environ.get('STREAMLIT_SERVER_PORT') and not os.environ.get('STREAMLIT_DEPLOYMENT'):
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run", 
                    "src/dashboard/app.py", 
                    "--server.port=8502",
                    "--server.address=localhost",
                    "--server.fileWatcherType=none"
                ], check=True)
            else:
                print("Cannot launch subprocess in deployment environment")
                return False
        except Exception as subprocess_error:
            print(f"Error with subprocess approach: {subprocess_error}")
            return False
    
    return True


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except FileNotFoundError:
        # Fall back to unittest if pytest is not available
        print("pytest not found, running with unittest...")
        try:
            result = subprocess.run([
                sys.executable, "tests/test_all.py"
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False


def show_status():
    """Show system status and data summary."""
    print("Vehicle Registration Dashboard Status")
    print("=" * 40)
    
    # Database status
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_summary_stats()
        
        print(f"Database Status: Connected")
        print(f"Total Records: {stats.get('total_records', 0):,}")
        print(f"Date Range: {stats.get('date_range', {}).get('start', 'N/A')} to {stats.get('date_range', {}).get('end', 'N/A')}")
        print(f"Total Registrations: {stats.get('total_registrations', 0):,}")
        print(f"Manufacturers: {stats.get('unique_manufacturers', 0)}")
        print(f"Categories: {stats.get('unique_categories', 0)}")
        
    except Exception as e:
        print(f"Database Status: Error - {e}")
    
    # File system status
    data_dir = Path("data")
    if data_dir.exists():
        raw_files = list(data_dir.glob("raw/*.csv"))
        processed_files = list(data_dir.glob("processed/*.csv"))
        
        print(f"\nData Files:")
        print(f"Raw files: {len(raw_files)}")
        print(f"Processed files: {len(processed_files)}")
    else:
        print("\nData directory not found")


def main():
    """Main function to handle command line arguments."""
    # Check if we're in a deployment environment (no CLI args)
    if len(sys.argv) == 1:
        # Default to dashboard mode for deployment
        print("No arguments provided - launching dashboard for deployment...")
        success = run_dashboard()
        if success:
            print("Dashboard launched successfully!")
        else:
            print("Dashboard launch failed!")
        return
    
    parser = argparse.ArgumentParser(
        description="Vehicle Registration Dashboard Management System"
    )
    
    parser.add_argument(
        'command',
        choices=['collect', 'process', 'dashboard', 'test', 'status'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    # Execute command
    success = False
    
    if args.command == 'collect':
        success = run_data_collection()
    elif args.command == 'process':
        success = run_data_processing()
    elif args.command == 'dashboard':
        success = run_dashboard()
    elif args.command == 'test':
        success = run_tests()
    elif args.command == 'status':
        show_status()
        success = True
    
    if success:
        print(f"\nCommand '{args.command}' completed successfully!")
        sys.exit(0)
    else:
        print(f"\nCommand '{args.command}' failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
