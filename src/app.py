import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import DATABASE_PATH
from sub_apps import (
    outlet_performance, 
    order_analysis, 
    coverage_analysis, 
    data_export, 
    comparative_analysis,
    store_coverage_universe,
    store_coverage_tc_utc,
    store_coverage_untouched,
    order_performance_pc_upc,
    order_performance_order_value,
    order_performance_positive_growth,
    order_performance_stopped_ordering,
    non_compliance_late_reporting,
    non_compliance_ovc_calls
)
from utils import initialize_filters, get_database_connection

# Set pandas option to avoid FutureWarning
pd.set_option('future.no_silent_downcasting', True)

# Set page configuration
st.set_page_config(
    page_title="Field Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# App title
st.title("Field Sales Performance Dashboard")

# Initialize filters
initialize_filters()

# Get database connection - keep it open for the app's lifecycle
con = get_database_connection()

# Main dashboard
st.header("Key Performance Indicators")

# KPIs
col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

try:
    # Total outlets
    total_outlets = con.execute("SELECT COUNT(*) FROM outlets").fetchone()[0]
    col1.metric("Total Outlets", total_outlets)
    
    # Filtered outlets
    filtered_outlets_query = """
        SELECT COUNT(*)
        FROM outlets o
    """
    
    # Add filters
    outlet_filter_conditions = []
    if st.session_state.selected_region != "All Regions":
        outlet_filter_conditions.append(f"o.region = '{st.session_state.selected_region}'")
    if st.session_state.selected_channel != "All Channels":
        outlet_filter_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
    if st.session_state.selected_l1_position != "All L1 Positions":
        outlet_filter_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
    if st.session_state.selected_l2_position != "All L2 Positions":
        outlet_filter_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
    if st.session_state.selected_l3_position != "All L3 Positions":
        outlet_filter_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
    if st.session_state.selected_beat != "All Beats":
        outlet_filter_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
    
    if outlet_filter_conditions:
        filtered_outlets_query += " WHERE " + " AND ".join(outlet_filter_conditions)
    
    filtered_outlets = con.execute(filtered_outlets_query).fetchone()[0] or 0
    col3.metric("Filtered Outlets", filtered_outlets)

    # Active outlets (with orders)
    active_outlets_query = """
        SELECT COUNT(DISTINCT o.outlet_id)
        FROM outlets o
        JOIN orders ord ON o.outlet_id = ord.outlet_id
    """
    
    # Add filters
    filter_conditions = []
    if st.session_state.date_range != "All Months":
        filter_conditions.append(f"ord.order_month = '{st.session_state.date_range}'")
    if st.session_state.selected_region != "All Regions":
        filter_conditions.append(f"o.region = '{st.session_state.selected_region}'")
    if st.session_state.selected_channel != "All Channels":
        filter_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
    if st.session_state.selected_l1_position != "All L1 Positions":
        filter_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
    if st.session_state.selected_l2_position != "All L2 Positions":
        filter_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
    if st.session_state.selected_l3_position != "All L3 Positions":
        filter_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
    if st.session_state.selected_beat != "All Beats":
        filter_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
    
    if filter_conditions:
        active_outlets_query += " WHERE " + " AND ".join(filter_conditions)
    
    active_outlets = con.execute(active_outlets_query).fetchone()[0] or 0
    col4.metric("Ordering Outlets", active_outlets)

    # Filtered Active Outlets (where isBlocked = "No")
    non_blocked_outlets_query = """
        SELECT COUNT(DISTINCT o.outlet_id)
        FROM outlets o
        WHERE o.is_blocked = 'No'
    """
    
    # Add filters (excluding date range to count all active outlets with orders)
    filtered_active_conditions = []
    if st.session_state.selected_region != "All Regions":
        filtered_active_conditions.append(f"o.region = '{st.session_state.selected_region}'")
    if st.session_state.selected_channel != "All Channels":
        filtered_active_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
    if st.session_state.selected_l1_position != "All L1 Positions":
        filtered_active_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
    if st.session_state.selected_l2_position != "All L2 Positions":
        filtered_active_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
    if st.session_state.selected_l3_position != "All L3 Positions":
        filtered_active_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
    if st.session_state.selected_beat != "All Beats":
        filtered_active_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
    
    if filtered_active_conditions:
        non_blocked_outlets_query += " AND " + " AND ".join(filtered_active_conditions)
    
    non_blocked_outlets = con.execute(non_blocked_outlets_query).fetchone()[0] or 0
    col8.metric("Non-Blocked Outlets", non_blocked_outlets)

    # Reordering outlets (with >1 order)
    reordering_query = """
        SELECT COUNT(*)
        FROM (
            SELECT ord.outlet_id
            FROM orders ord
    """
    
    # Add filters
    reordering_conditions = []
    if st.session_state.date_range != "All Months":
        reordering_conditions.append(f"ord.order_month = '{st.session_state.date_range}'")
    if st.session_state.selected_region != "All Regions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{st.session_state.selected_region}')")
    if st.session_state.selected_channel != "All Channels":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{st.session_state.selected_channel}')")
    if st.session_state.selected_l1_position != "All L1 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{st.session_state.selected_l1_position}')")
    if st.session_state.selected_l2_position != "All L2 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{st.session_state.selected_l2_position}')")
    if st.session_state.selected_l3_position != "All L3 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{st.session_state.selected_l3_position}')")
    if st.session_state.selected_beat != "All Beats":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{st.session_state.selected_beat}')")
    
    if reordering_conditions:
        reordering_query += " WHERE " + " AND ".join(reordering_conditions)
    
    reordering_query += " GROUP BY ord.outlet_id HAVING COUNT(ord.order_id) > 1)"
    
    reordering_outlets = con.execute(reordering_query).fetchone()[0] or 0
    col5.metric("Reordering Outlets", reordering_outlets)

    # Coverage rate
    coverage_rate = 0
    if active_outlets > 0:
        coverage_rate = round((reordering_outlets / active_outlets) * 100, 2)
    col6.metric("Reorder Rate", f"{coverage_rate}%")

    # Visit count
    visit_count_query = """
        SELECT COUNT(DISTINCT v.visit_id)
        FROM visits v
    """
    
    # Add filters
    visit_filter_conditions = []
    if st.session_state.date_range != "All Months":
        visit_filter_conditions.append(f"v.visit_month = '{st.session_state.date_range}'")
    if st.session_state.selected_region != "All Regions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{st.session_state.selected_region}')")
    if st.session_state.selected_channel != "All Channels":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{st.session_state.selected_channel}')")
    if st.session_state.selected_l1_position != "All L1 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{st.session_state.selected_l1_position}')")
    if st.session_state.selected_l2_position != "All L2 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{st.session_state.selected_l2_position}')")
    if st.session_state.selected_l3_position != "All L3 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{st.session_state.selected_l3_position}')")
    if st.session_state.selected_beat != "All Beats":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{st.session_state.selected_beat}')")
    
    if visit_filter_conditions:
        visit_count_query += " WHERE " + " AND ".join(visit_filter_conditions)
    
    visit_count = con.execute(visit_count_query).fetchone()[0] or 0
    col7.metric("Visit Count", visit_count)

    # Unique L1 positions taking orders
    unique_l1_query = """
        SELECT COUNT(DISTINCT o.l1_position_name)
        FROM orders ord
        JOIN outlets o ON ord.outlet_id = o.outlet_id
    """
    
    # Add filters
    l1_filter_conditions = []
    if st.session_state.date_range != "All Months":
        l1_filter_conditions.append(f"ord.order_month = '{st.session_state.date_range}'")
    if st.session_state.selected_region != "All Regions":
        l1_filter_conditions.append(f"o.region = '{st.session_state.selected_region}'")
    if st.session_state.selected_channel != "All Channels":
        l1_filter_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
    if st.session_state.selected_l1_position != "All L1 Positions":
        l1_filter_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
    if st.session_state.selected_l2_position != "All L2 Positions":
        l1_filter_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
    if st.session_state.selected_l3_position != "All L3 Positions":
        l1_filter_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
    if st.session_state.selected_beat != "All Beats":
        l1_filter_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
    
    if l1_filter_conditions:
        unique_l1_query += " WHERE " + " AND ".join(l1_filter_conditions)
    
    unique_l1_count = con.execute(unique_l1_query).fetchone()[0] or 0
    col2.metric("Unique L1 Positions", unique_l1_count)
except Exception as e:
    st.error(f"Error calculating KPIs: {e}")

# Setup navigation using Streamlit selectbox as a fallback
st.header("Reporting Modules")
app_options = [
    "Outlet Performance",
    "Order Analysis",
    "Coverage Analysis",
    "Data Export",
    "Comparative Analysis",
    "Store Coverage - Universe",
    "Store Coverage - TC & UTC Unique",
    "Store Coverage - Untouched Stores",
    "Order Performance - PC & UPC Unique",
    "Order Performance - Order Value",
    "Order Performance - Positive Growth PCs",
    "Order Performance - Stopped Ordering TCs",
    "Non-Compliance - Late Reporting",
    "Non-Compliance - OVC Calls"
]
selected_app = st.selectbox("Select a Reporting Module", app_options)

# Map selection to corresponding app function
app_mapping = {
    "Outlet Performance": outlet_performance.app,
    "Order Analysis": order_analysis.app,
    "Coverage Analysis": coverage_analysis.app,
    "Data Export": data_export.app,
    "Comparative Analysis": comparative_analysis.app,
    "Store Coverage - Universe": store_coverage_universe.app,
    "Store Coverage - TC & UTC Unique": store_coverage_tc_utc.app,
    "Store Coverage - Untouched Stores": store_coverage_untouched.app,
    "Order Performance - PC & UPC Unique": order_performance_pc_upc.app,
    "Order Performance - Order Value": order_performance_order_value.app,
    "Order Performance - Positive Growth PCs": order_performance_positive_growth.app,
    "Order Performance - Stopped Ordering TCs": order_performance_stopped_ordering.app,
    "Non-Compliance - Late Reporting": non_compliance_late_reporting.app,
    "Non-Compliance - OVC Calls": non_compliance_ovc_calls.app
}

# Execute the selected app
app_mapping[selected_app]()

# Note: Do not close the connection here to avoid "Connection already closed" errors
# The connection will be managed by Streamlit's cache_resource decorator in utils.py