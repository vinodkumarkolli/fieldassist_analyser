# Field Sales Performance Analysis Dashboard

This project provides a comprehensive analysis of field sales team performance using DuckDB for data processing and Streamlit for visualization.

## Features

- Outlet performance analysis
- Order frequency and value tracking
- Outlet categorization based on performance
- Coverage analysis (visits vs. orders)
- Interactive dashboard with filtering capabilities
- Data export functionality

## Project Structure

```
.
├── data/                   # Processed data storage
├── src/                    # Source code
│   ├── app.py             # Main Streamlit application
│   ├── config.py          # Configuration settings
│   └── data_processing.py # Data processing module
├── Outlets/               # Outlet data files
├── Secondary Orders/      # Secondary sales order files
├── Visits/                # Visit data files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup Instructions

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure data files are in place:**
   - Place outlet data files in the `Outlets/` directory
   - Place secondary order files in the `Secondary Orders/` directory
   - Place visit data files in the `Visits/` directory

3. **Process the data:**
   ```bash
   python src/data_processing.py
   ```

4. **Run the dashboard:**
   ```bash
   streamlit run src/app.py
   ```

## Dashboard Features

### Filters
- Date range selection
- Region filtering
- Channel filtering

### Analysis Tabs
1. **Outlet Performance**: Scatter plots and category distribution
2. **Order Analysis**: Top outlets and order trends
3. **Coverage Analysis**: Visit metrics and coverage gaps
4. **Data Export**: Download filtered data as CSV

## Data Processing

The data processing module (`src/data_processing.py`) handles:
- Reading Excel files from all three data sources
- Creating and populating DuckDB tables
- Calculating outlet metrics
- Analyzing coverage patterns

## Requirements

- Python 3.8 or higher
- DuckDB
- Streamlit
- Pandas
- OpenPyXL
- Plotly

## Usage

1. Place your Excel files in the appropriate directories
2. Run the data processing script to populate the database
3. Start the Streamlit dashboard
4. Use the filters to analyze specific time periods or regions
5. Export data as needed using the Data Export tab

## Customization

You can customize the dashboard by modifying:
- `src/app.py`: Dashboard layout and visualizations
- `src/config.py`: Configuration settings
- `src/data_processing.py`: Data processing logic