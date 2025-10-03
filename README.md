# Field Sales Performance Dashboard

A Streamlit-based application for analyzing field sales performance data, with modular sub-apps for various reporting aspects.

## Overview

This dashboard provides insights into field sales performance through Key Performance Indicators (KPIs) and detailed reporting modules. The application uses DuckDB as the backend database to process data from outlets, orders, and visits.

## Project Structure

The application has been restructured to use `streamlit-launchpad` for navigation, breaking down the monolithic app into modular sub-apps for better maintainability and scalability.

### Directory Structure

- **src/**: Contains the main application and utility scripts.
  - **app.py**: The main entry point of the application, displaying KPIs and providing navigation to sub-apps via Streamlit Launchpad.
  - **config.py**: Configuration file with paths and table names.
  - **data_processing.py**: Scripts for loading and processing data into DuckDB.
  - **data_reload.py**: Utility to reload data into the database.
  - **utils.py**: Utility functions for common tasks like database connection and filter management.
  - **sub_apps/**: Directory containing individual reporting modules as separate Streamlit apps.
    - **outlet_performance.py**: Analysis of outlet performance metrics.
    - **order_analysis.py**: Detailed analysis of order data.
    - **coverage_analysis.py**: Coverage metrics and analysis.
    - **data_export.py**: Export filtered data to CSV.
    - **comparative_analysis.py**: Comparative analysis with uploaded data.
    - **store_coverage_universe.py**: Reporting on the total universe of stores.
    - **store_coverage_tc_utc.py**: Reporting on Total Coverage (TC) and Unique Transaction Coverage (UTC).
    - **store_coverage_untouched.py**: Reporting on untouched stores for This Month (TM), Last Month (LM), and Last 3 Months (L3M).
    - **order_performance_pc_upc.py**: Reporting on Productive Calls (PC) and Unique Productive Calls (UPC).
    - **order_performance_order_value.py**: Reporting on Total Order Value, Average Order Value, and top 10% contributors.
    - **order_performance_positive_growth.py**: Reporting on outlets with positive growth compared to last month and historical average.
    - **order_performance_stopped_ordering.py**: Reporting on TCs that stopped ordering in LM and L3M.
    - **non_compliance_late_reporting.py**: Reporting on late reporting instances.
    - **non_compliance_ovc_calls.py**: Reporting on Order Verification Calls non-compliance.

### Data Directories

- **Outlets/**: Contains Excel files with outlet data.
- **Secondary Orders/**: Contains Excel files with order data.
- **Visits/**: Contains Excel files with visit data.
- **data/**: Directory for the DuckDB database file.

## Installation

1. Clone the repository or download the project files.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the data processing script to load data into DuckDB (if not already done):
   ```
   python src/data_processing.py
   ```
4. Start the Streamlit application:
   ```
   streamlit run src/app.py
   ```

## Usage

- **Filters**: Use the sidebar to apply filters on region, channel, positions (L1, L2, L3), beat, and date range. These filters apply across all sub-apps.
- **KPIs**: View key performance indicators at the top of the main dashboard.
- **Navigation**: Use the Streamlit Launchpad interface to navigate between different reporting modules. Each module focuses on a specific aspect of sales performance.

## Reporting Modules

### Existing Modules
- **Outlet Performance**: Scatter plots and category distribution of outlets based on order frequency and value.
- **Order Analysis**: Top outlets by order value and trend analysis over time.
- **Coverage Analysis**: Metrics on coverage and visited vs. non-visited outlets.
- **Data Export**: Export filtered data to CSV format.
- **Comparative Analysis**: Upload external data for comparison with historical sales data.

### Store Coverage
- **Universe**: Total number of stores with regional breakdown.
- **TC & UTC Unique**: Total Coverage and Unique Transaction Coverage metrics.
- **Untouched Stores (TM, LM, L3M)**: Stores without orders in the current month, last month, and last 3 months.

### Order Performance
- **PC & UPC Unique**: Productive Calls and Unique Productive Calls metrics.
- **Order Value**: Total and average order values, plus outlets contributing to the top 10% of order value.
- **Positive Growth PCs**: Outlets showing positive growth compared to last month and historical average.
- **Stopped Ordering TCs**: TCs (L1 positions) that stopped ordering in the current month compared to LM and L3M.

### Non-Compliance
- **Late Reporting**: Instances of late reporting for visits and orders.
- **OVC Calls**: Non-compliance related to Order Verification Calls for high-value orders.

## Data Processing

To reload or update data:
- Run `python src/data_reload.py` to reload all data.
- Run specific functions within `data_reload.py` to reload specific datasets (e.g., visits only).

## Contributing

For contributions, bug reports, or feature requests, please contact the project maintainers or submit issues/pull requests to the repository if applicable.

## License

This project is licensed under [insert license information if applicable].