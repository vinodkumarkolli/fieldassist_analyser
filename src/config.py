# Configuration file for the sales performance analysis project

import os

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