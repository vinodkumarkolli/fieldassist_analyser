import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from data_processing import load_visits_data, initialize_database, load_outlets_data, load_orders_data, calculate_outlet_metrics, analyze_coverage, update_outlets_with_orders_data

def reload_visits_data():
    """Reload only the visits data"""
    print("Reloading visits data...")
    
    # Load visits data
    load_visits_data()
    
    # Recalculate coverage analysis
    print("Recalculating coverage analysis...")
    analyze_coverage()
    
    print("Visits data reloaded successfully!")

def reload_all_data():
    """Reload all data"""
    print("Reloading all data...")
    
    # Initialize database
    initialize_database()
    
    # Load all data
    load_outlets_data()
    load_orders_data()
    load_visits_data()
    
    # Update outlets with orders data
    update_outlets_with_orders_data()
    
    # Calculate metrics
    calculate_outlet_metrics()
    analyze_coverage()
    
    print("All data reloaded successfully!")

if __name__ == "__main__":
    # By default, reload all data
    reload_all_data()