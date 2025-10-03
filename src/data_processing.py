import pandas as pd
import duckdb
import os
import glob
import re
from datetime import datetime

# Define paths to data directories
OUTLETS_DIR = "Outlets"
SECONDARY_ORDERS_DIR = "Secondary Orders"
VISITS_DIR = "Visits"
DATABASE_PATH = "data/sales_performance.duckdb"

# Define table names
OUTLETS_TABLE = "outlets"
ORDERS_TABLE = "orders"
VISITS_TABLE = "visits"

# Define metrics table names
OUTLET_METRICS_TABLE = "outlet_metrics"
COVERAGE_ANALYSIS_TABLE = "coverage_analysis"

# Define date format used in file names
DATE_FORMAT = "%d-%m-%y"

def initialize_database():
    """Initialize DuckDB database and create tables"""
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # Connect to DuckDB
    con = duckdb.connect(DATABASE_PATH)
    
    # Create tables with additional columns for filtering
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {OUTLETS_TABLE} (
            outlet_id VARCHAR,
            outlet_name VARCHAR,
            region VARCHAR,
            state VARCHAR,
            city VARCHAR,
            channel VARCHAR,
            outlet_type VARCHAR,
            l1_position_name VARCHAR,
            l2_position_name VARCHAR,
            l3_position_name VARCHAR,
            beat VARCHAR,
            outlet_creation_date DATE,
            is_blocked VARCHAR
        )
    """)
    
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {ORDERS_TABLE} (
            order_id VARCHAR,
            outlet_id VARCHAR,
            order_date DATE,
            product_name VARCHAR,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            total_amount DECIMAL(10,2),
            order_month VARCHAR,
            l1_position_name VARCHAR,
            l2_position_name VARCHAR,
            l3_position_name VARCHAR,
            beat VARCHAR
        )
    """)
    
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {VISITS_TABLE} (
            visit_id VARCHAR,
            outlet_id VARCHAR,
            visit_date DATE,
            salesperson_id VARCHAR,
            visit_month VARCHAR
        )
    """)
    
    # Add outlet_creation_date and is_blocked columns if they don't exist
    try:
        con.execute(f"ALTER TABLE {OUTLETS_TABLE} ADD COLUMN outlet_creation_date DATE")
        print("Added outlet_creation_date column to outlets table")
    except Exception as e:
        # Column might already exist, which is fine
        pass
        
    try:
        con.execute(f"ALTER TABLE {OUTLETS_TABLE} ADD COLUMN is_blocked VARCHAR")
        print("Added is_blocked column to outlets table")
    except Exception as e:
        # Column might already exist, which is fine
        pass
    
    con.close()
    print("Database initialized successfully")

def load_outlets_data():
    """Load outlets data from Excel files"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Clear existing data
    con.execute(f"DELETE FROM {OUTLETS_TABLE}")
    
    # Find the outlets file
    outlets_files = glob.glob(os.path.join(OUTLETS_DIR, "*.xlsx"))
    
    if not outlets_files:
        print("No outlets files found")
        con.close()
        return
    
    # For now, we'll assume there's only one outlets file
    outlets_file = outlets_files[0]
    print(f"Loading outlets data from {outlets_file}")
    
    # Read the Excel file
    try:
        df = pd.read_excel(outlets_file, sheet_name=0)
        print(f"Loaded {len(df)} outlet records")
        
        # Map the actual column names to our schema
        mapped_df = pd.DataFrame()
        mapped_df['outlet_id'] = df['Outlet Erp Id'] if 'Outlet Erp Id' in df.columns else None
        mapped_df['outlet_name'] = df['Outlets Name'] if 'Outlets Name' in df.columns else None
        mapped_df['region'] = df['Region'] if 'Region' in df.columns else None
        mapped_df['state'] = df['State'] if 'State' in df.columns else None
        mapped_df['city'] = df['City'] if 'City' in df.columns else None
        mapped_df['channel'] = df['Outlets Channel'] if 'Outlets Channel' in df.columns else None
        mapped_df['outlet_type'] = df['Outlet Type'] if 'Outlet Type' in df.columns else None
        mapped_df['l1_position_name'] = df['L1 Position Name'] if 'L1 Position Name' in df.columns else None
        mapped_df['l2_position_name'] = None  # This will be updated later
        mapped_df['l3_position_name'] = None  # This will be updated later
        mapped_df['beat'] = df['Beats'] if 'Beats' in df.columns else None
        mapped_df['outlet_creation_date'] = df['Outlet Creation Date'] if 'Outlet Creation Date' in df.columns else None
        mapped_df['is_blocked'] = df['IsBlocked'] if 'IsBlocked' in df.columns else None
        
        # Remove rows with null outlet_id
        mapped_df = mapped_df.dropna(subset=['outlet_id'])
        
        # For now, we'll just insert the data as is
        con.register('outlets_df', mapped_df)
        con.execute(f"INSERT INTO {OUTLETS_TABLE} SELECT * FROM outlets_df")
        
        print(f"Successfully loaded {con.execute(f'SELECT COUNT(*) FROM {OUTLETS_TABLE}').fetchone()[0]} outlets")
    except Exception as e:
        print(f"Error loading outlets data: {e}")
    
    con.close()

def load_orders_data():
    """Load orders data from Excel files"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Clear existing data
    con.execute(f"DELETE FROM {ORDERS_TABLE}")
    
    # Find all orders files
    orders_files = glob.glob(os.path.join(SECONDARY_ORDERS_DIR, "*.xlsx"))
    
    if not orders_files:
        print("No orders files found")
        con.close()
        return
    
    print(f"Found {len(orders_files)} orders files")
    
    total_orders_loaded = 0
    
    for file_path in orders_files:
        print(f"Processing {file_path}")
        
        try:
            # Extract date range from filename
            filename = os.path.basename(file_path)
            date_match = re.search(r'(\d{2}-\d{2}-\d{2}) to (\d{2}-\d{2}-\d{2})', filename)
            
            if date_match:
                start_date_str = date_match.group(1)
                # For now, we'll just use the start date to determine the month
                month_str = start_date_str[3:5] + "-" + start_date_str[6:]  # MM-YY format
            else:
                month_str = "unknown"
            
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            print(f"Loaded {len(df)} order records from {filename}")
            
            # Map the actual column names to our schema
            mapped_df = pd.DataFrame()
            mapped_df['order_id'] = df['Order No'] if 'Order No' in df.columns else None
            mapped_df['outlet_id'] = df['Outlet Erp Id'] if 'Outlet Erp Id' in df.columns else None
            mapped_df['order_date'] = df['Order Date'] if 'Order Date' in df.columns else None
            mapped_df['product_name'] = df['Product'] if 'Product' in df.columns else None
            mapped_df['quantity'] = df['Qty ( Unit )'] if 'Qty ( Unit )' in df.columns else None
            mapped_df['unit_price'] = df['Price'] if 'Price' in df.columns else None
            mapped_df['total_amount'] = df['Net Value Tax Inclusive'] if 'Net Value Tax Inclusive' in df.columns else None
            mapped_df['order_month'] = month_str
            mapped_df['l1_position_name'] = df['L1Position'] if 'L1Position' in df.columns else None
            mapped_df['l2_position_name'] = df['L2Position'] if 'L2Position' in df.columns else None
            mapped_df['l3_position_name'] = df['L3Position'] if 'L3Position' in df.columns else None
            mapped_df['beat'] = df['Beat'] if 'Beat' in df.columns else None
            
            # Remove rows with null outlet_id or order_id
            mapped_df = mapped_df.dropna(subset=['outlet_id', 'order_id'])
            
            # Only include orders with Sale Value > 0
            if 'Sale Value' in df.columns:
                mapped_df = mapped_df[df['Sale Value'] > 0]
            
            # Convert data types
            mapped_df['quantity'] = pd.to_numeric(mapped_df['quantity'], errors='coerce').fillna(0).astype(int)
            mapped_df['unit_price'] = pd.to_numeric(mapped_df['unit_price'], errors='coerce').fillna(0)
            mapped_df['total_amount'] = pd.to_numeric(mapped_df['total_amount'], errors='coerce').fillna(0)
            
            # For now, we'll just insert the data as is
            con.register('orders_df', mapped_df)
            con.execute(f"INSERT INTO {ORDERS_TABLE} SELECT * FROM orders_df")
            
            total_orders_loaded += len(mapped_df)
            print(f"Successfully loaded {len(mapped_df)} orders from {filename}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    total_orders = con.execute(f"SELECT COUNT(*) FROM {ORDERS_TABLE}").fetchone()[0]
    print(f"Successfully loaded {total_orders} total orders")
    con.close()

def load_visits_data():
    """Load visits data from Excel files"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Clear existing data
    con.execute(f"DELETE FROM {VISITS_TABLE}")
    
    # Find all visits files
    visits_files = glob.glob(os.path.join(VISITS_DIR, "*.xlsx"))
    
    if not visits_files:
        print("No visits files found")
        con.close()
        return
    
    print(f"Found {len(visits_files)} visits files")
    
    total_visits_loaded = 0
    
    for file_path in visits_files:
        print(f"Processing {file_path}")
        
        try:
            # Extract date range from filename
            filename = os.path.basename(file_path)
            date_match = re.search(r'(\d{2}-\d{2}-\d{2}) to (\d{2}-\d{2}-\d{2})', filename)
            
            if date_match:
                start_date_str = date_match.group(1)
                # For now, we'll just use the start date to determine the month
                month_str = start_date_str[3:5] + "-" + start_date_str[6:]  # MM-YY format
            else:
                month_str = "unknown"
            
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            print(f"Loaded {len(df)} visit records from {filename}")
            
            # Map the actual column names to our schema
            mapped_df = pd.DataFrame()
            mapped_df['visit_id'] = df['Order No'] if 'Order No' in df.columns else None
            mapped_df['outlet_id'] = df['Outlets Erp Id'] if 'Outlets Erp Id' in df.columns else None
            mapped_df['visit_date'] = None  # We don't have visit date in this data
            mapped_df['salesperson_id'] = df['User'] if 'User' in df.columns else None
            mapped_df['visit_month'] = month_str
            
            # Remove rows with null outlet_id or visit_id
            mapped_df = mapped_df.dropna(subset=['outlet_id', 'visit_id'])
            
            # For now, we'll just insert the data as is
            con.register('visits_df', mapped_df)
            con.execute(f"INSERT INTO {VISITS_TABLE} SELECT * FROM visits_df")
            
            total_visits_loaded += len(mapped_df)
            print(f"Successfully loaded {len(mapped_df)} visits from {filename}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    total_visits = con.execute(f"SELECT COUNT(*) FROM {VISITS_TABLE}").fetchone()[0]
    print(f"Successfully loaded {total_visits} total visits")
    con.close()

def update_outlets_with_orders_data():
    """Update outlets table with L2 and L3 positions from orders data"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Update outlets table with L2 and L3 positions from orders data
    con.execute(f"""
        UPDATE {OUTLETS_TABLE} 
        SET l2_position_name = (
            SELECT DISTINCT o.l2_position_name 
            FROM {ORDERS_TABLE} o 
            WHERE o.outlet_id = {OUTLETS_TABLE}.outlet_id 
            AND o.l2_position_name IS NOT NULL 
            LIMIT 1
        ),
        l3_position_name = (
            SELECT DISTINCT o.l3_position_name 
            FROM {ORDERS_TABLE} o 
            WHERE o.outlet_id = {OUTLETS_TABLE}.outlet_id 
            AND o.l3_position_name IS NOT NULL 
            LIMIT 1
        )
        WHERE outlet_id IN (
            SELECT DISTINCT outlet_id 
            FROM {ORDERS_TABLE} 
            WHERE l2_position_name IS NOT NULL OR l3_position_name IS NOT NULL
        )
    """)
    
    print("Updated outlets table with L2 and L3 positions from orders data")
    con.close()

def calculate_outlet_metrics():
    """Calculate outlet metrics and store in a table"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Create outlet metrics table
    con.execute(f"""
        CREATE OR REPLACE TABLE {OUTLET_METRICS_TABLE} AS
        SELECT 
            o.outlet_id,
            o.outlet_name,
            o.region,
            o.state,
            o.city,
            o.channel,
            o.outlet_type,
            o.l1_position_name,
            o.l2_position_name,
            o.l3_position_name,
            o.beat,
            COUNT(ord.order_id) as total_orders,
            SUM(ord.total_amount) as total_order_value,
            AVG(ord.total_amount) as avg_order_value,
            MIN(ord.order_date) as first_order_date,
            MAX(ord.order_date) as last_order_date
        FROM {OUTLETS_TABLE} o
        LEFT JOIN {ORDERS_TABLE} ord ON o.outlet_id = ord.outlet_id
        GROUP BY o.outlet_id, o.outlet_name, o.region, o.state, o.city, o.channel, o.outlet_type, 
                 o.l1_position_name, o.l2_position_name, o.l3_position_name, o.beat
    """)
    
    metrics_count = con.execute(f"SELECT COUNT(*) FROM {OUTLET_METRICS_TABLE}").fetchone()[0]
    print(f"Calculated metrics for {metrics_count} outlets")
    con.close()

def analyze_coverage():
    """Analyze coverage by joining orders and visits data"""
    con = duckdb.connect(DATABASE_PATH)
    
    # Create coverage analysis table
    con.execute(f"""
        CREATE OR REPLACE TABLE {COVERAGE_ANALYSIS_TABLE} AS
        SELECT 
            om.*,
            CASE 
                WHEN om.total_orders > 1 THEN 'Reordering'
                WHEN om.total_orders = 1 THEN 'One-time'
                ELSE 'No Orders'
            END as order_category,
            COUNT(v.visit_id) as total_visits
        FROM {OUTLET_METRICS_TABLE} om
        LEFT JOIN {VISITS_TABLE} v ON om.outlet_id = v.outlet_id
        GROUP BY ALL
    """)
    
    coverage_count = con.execute(f"SELECT COUNT(*) FROM {COVERAGE_ANALYSIS_TABLE}").fetchone()[0]
    print(f"Analyzed coverage for {coverage_count} outlets")
    con.close()

def process_all_data():
    """Process all data files and calculate metrics"""
    print("Initializing database...")
    initialize_database()
    
    print("Loading outlets data...")
    load_outlets_data()
    
    print("Loading orders data...")
    load_orders_data()
    
    print("Loading visits data...")
    load_visits_data()
    
    print("Updating outlets with orders data...")
    update_outlets_with_orders_data()
    
    print("Calculating outlet metrics...")
    calculate_outlet_metrics()
    
    print("Analyzing coverage...")
    analyze_coverage()
    
    print("Data processing complete!")

if __name__ == "__main__":
    process_all_data()