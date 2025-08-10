"""
Database Operations Module

This module provides database connectivity and operations for storing
and retrieving vehicle registration data.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages SQLite database operations for vehicle registration data.
    """
    
    def __init__(self, db_path: str = "data/vehicle_registrations.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Vehicle registrations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    year INTEGER NOT NULL,
                    quarter TEXT NOT NULL,
                    month TEXT NOT NULL,
                    vehicle_category TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    registrations INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, vehicle_category, manufacturer)
                )
            """)
            
            # Growth metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS growth_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_type TEXT NOT NULL, -- 'yearly', 'quarterly', 'monthly'
                    period_value TEXT NOT NULL,
                    vehicle_category TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    registrations INTEGER NOT NULL,
                    growth_rate_pct REAL,
                    growth_rate_abs INTEGER,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(period_type, period_value, vehicle_category, manufacturer)
                )
            """)
            
            # Market share table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS market_share (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period_type TEXT NOT NULL,
                    period_value TEXT NOT NULL,
                    vehicle_category TEXT NOT NULL,
                    manufacturer TEXT NOT NULL,
                    registrations INTEGER NOT NULL,
                    market_share_pct REAL NOT NULL,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(period_type, period_value, vehicle_category, manufacturer)
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_registrations_date ON vehicle_registrations(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_registrations_category ON vehicle_registrations(vehicle_category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_registrations_manufacturer ON vehicle_registrations(manufacturer)")
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_vehicle_data(self, df: pd.DataFrame, replace: bool = False) -> int:
        """
        Insert vehicle registration data into database.
        
        Args:
            df: DataFrame containing vehicle registration data
            replace: If True, replace existing data; if False, ignore duplicates
            
        Returns:
            Number of rows inserted
        """
        # Ensure required columns exist
        required_columns = ['date', 'year', 'quarter', 'month', 'vehicle_category', 'manufacturer', 'registrations']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Prepare data
        data_to_insert = df[required_columns].copy()
        data_to_insert['date'] = pd.to_datetime(data_to_insert['date']).dt.strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                if replace:
                    # Use REPLACE to handle duplicates
                    rows_affected = data_to_insert.to_sql(
                        'vehicle_registrations',
                        conn,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                else:
                    # Use INSERT OR IGNORE to handle duplicates
                    rows_affected = 0
                    for _, row in data_to_insert.iterrows():
                        try:
                            conn.execute("""
                                INSERT OR IGNORE INTO vehicle_registrations 
                                (date, year, quarter, month, vehicle_category, manufacturer, registrations)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, tuple(row))
                            rows_affected += conn.total_changes
                        except sqlite3.Error as e:
                            logger.warning(f"Error inserting row: {e}")
                
                conn.commit()
                logger.info(f"Inserted {rows_affected} records into vehicle_registrations table")
                return rows_affected
                
        except Exception as e:
            logger.error(f"Error inserting vehicle data: {e}")
            raise
    
    def get_vehicle_data(self, 
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        vehicle_categories: Optional[List[str]] = None,
                        manufacturers: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retrieve vehicle registration data from database.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            vehicle_categories: List of vehicle categories to filter
            manufacturers: List of manufacturers to filter
            
        Returns:
            DataFrame containing filtered vehicle registration data
        """
        query = "SELECT * FROM vehicle_registrations WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        if vehicle_categories:
            placeholders = ','.join(['?' for _ in vehicle_categories])
            query += f" AND vehicle_category IN ({placeholders})"
            params.extend(vehicle_categories)
        
        if manufacturers:
            placeholders = ','.join(['?' for _ in manufacturers])
            query += f" AND manufacturer IN ({placeholders})"
            params.extend(manufacturers)
        
        query += " ORDER BY date, vehicle_category, manufacturer"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                logger.info(f"Retrieved {len(df)} records from database")
                return df
        except Exception as e:
            logger.error(f"Error retrieving vehicle data: {e}")
            return pd.DataFrame()
    
    def store_growth_metrics(self, growth_data: pd.DataFrame, period_type: str) -> int:
        """
        Store calculated growth metrics in database.
        
        Args:
            growth_data: DataFrame containing growth calculations
            period_type: Type of period ('yearly', 'quarterly', 'monthly')
            
        Returns:
            Number of rows inserted
        """
        if growth_data.empty:
            return 0
        
        # Prepare data based on period type
        if period_type == 'yearly':
            period_col = 'year'
        elif period_type == 'quarterly':
            period_col = 'quarter_id'
        else:
            period_col = 'month'
        
        data_to_insert = []
        for _, row in growth_data.iterrows():
            if period_type == 'yearly':
                growth_pct_col = 'yoy_growth_pct'
                growth_abs_col = 'yoy_growth_abs'
            elif period_type == 'quarterly':
                growth_pct_col = 'qoq_growth_pct'
                growth_abs_col = 'qoq_growth_abs'
            else:
                growth_pct_col = 'mom_growth_pct'
                growth_abs_col = 'mom_growth_abs'
            
            if growth_pct_col in row and not pd.isna(row[growth_pct_col]):
                data_to_insert.append({
                    'period_type': period_type,
                    'period_value': str(row[period_col]),
                    'vehicle_category': row['vehicle_category'],
                    'manufacturer': row['manufacturer'],
                    'registrations': row['registrations'],
                    'growth_rate_pct': row[growth_pct_col],
                    'growth_rate_abs': row.get(growth_abs_col, 0)
                })
        
        if not data_to_insert:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for record in data_to_insert:
                    conn.execute("""
                        INSERT OR REPLACE INTO growth_metrics 
                        (period_type, period_value, vehicle_category, manufacturer, 
                         registrations, growth_rate_pct, growth_rate_abs)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['period_type'],
                        record['period_value'],
                        record['vehicle_category'],
                        record['manufacturer'],
                        record['registrations'],
                        record['growth_rate_pct'],
                        record['growth_rate_abs']
                    ))
                
                conn.commit()
                logger.info(f"Stored {len(data_to_insert)} growth metrics records")
                return len(data_to_insert)
                
        except Exception as e:
            logger.error(f"Error storing growth metrics: {e}")
            return 0
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics from the database.
        
        Returns:
            Dictionary containing summary statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total records
                total_records = conn.execute("SELECT COUNT(*) FROM vehicle_registrations").fetchone()[0]
                
                # Date range
                date_range = conn.execute("""
                    SELECT MIN(date), MAX(date) FROM vehicle_registrations
                """).fetchone()
                
                # Total registrations
                total_registrations = conn.execute("""
                    SELECT SUM(registrations) FROM vehicle_registrations
                """).fetchone()[0] or 0
                
                # Unique manufacturers and categories
                unique_manufacturers = conn.execute("""
                    SELECT COUNT(DISTINCT manufacturer) FROM vehicle_registrations
                """).fetchone()[0]
                
                unique_categories = conn.execute("""
                    SELECT COUNT(DISTINCT vehicle_category) FROM vehicle_registrations
                """).fetchone()[0]
                
                # Top manufacturer
                top_manufacturer = conn.execute("""
                    SELECT manufacturer, SUM(registrations) as total
                    FROM vehicle_registrations
                    GROUP BY manufacturer
                    ORDER BY total DESC
                    LIMIT 1
                """).fetchone()
                
                return {
                    'total_records': total_records,
                    'date_range': {
                        'start': date_range[0] if date_range[0] else None,
                        'end': date_range[1] if date_range[1] else None
                    },
                    'total_registrations': total_registrations,
                    'unique_manufacturers': unique_manufacturers,
                    'unique_categories': unique_categories,
                    'top_manufacturer': {
                        'name': top_manufacturer[0] if top_manufacturer else None,
                        'registrations': top_manufacturer[1] if top_manufacturer else 0
                    },
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting summary stats: {e}")
            return {}
    
    def execute_custom_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Execute a custom SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            params: Optional list of parameters for the query
            
        Returns:
            DataFrame containing query results
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params or [])
                return df
        except Exception as e:
            logger.error(f"Error executing custom query: {e}")
            return pd.DataFrame()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path for the backup file
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def close(self) -> None:
        """Close database connections (placeholder for connection pooling)."""
        logger.info("Database manager closed")


# Example usage and testing
def main():
    """Test the database manager functionality."""
    db_manager = DatabaseManager()
    
    # Get summary stats
    stats = db_manager.get_summary_stats()
    print("Database Summary:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test custom query
    query = """
        SELECT vehicle_category, COUNT(*) as record_count, SUM(registrations) as total_registrations
        FROM vehicle_registrations
        GROUP BY vehicle_category
        ORDER BY total_registrations DESC
    """
    
    results = db_manager.execute_custom_query(query)
    if not results.empty:
        print("\nVehicle Category Summary:")
        print(results.to_string(index=False))


if __name__ == "__main__":
    main()
