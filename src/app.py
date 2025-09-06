import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import *

# Set page configuration
st.set_page_config(
    page_title="Field Sales Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize connection to DuckDB
@st.cache_resource
def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

# App title
st.title("Field Sales Performance Dashboard")

# Get database connection
con = get_database_connection()

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
if "date_range" not in st.session_state:
    st.session_state.date_range = "All Months"
date_range = st.sidebar.selectbox(
    "Select Month Range",
    ["All Months", "01-25", "02-25", "03-25", "04-25", "05-25", "06-25", "07-25", "08-25"],
    index=["All Months", "01-25", "02-25", "03-25", "04-25", "05-25", "06-25", "07-25", "08-25"].index(st.session_state.date_range) if st.session_state.date_range in ["All Months", "01-25", "02-25", "03-25", "04-25", "05-25", "06-25", "07-25", "08-25"] else 0
)
st.session_state.date_range = date_range

# Region filter
try:
    regions = con.execute("SELECT DISTINCT region FROM outlets").fetchall()
    regions = [row[0] for row in regions if row[0] is not None]
    regions.sort()  # Sort the regions to ensure consistent order
    regions.insert(0, "All Regions")
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = "All Regions"
    selected_region = st.sidebar.selectbox(
        "Select Region",
        regions,
        index=regions.index(st.session_state.selected_region) if st.session_state.selected_region in regions else 0
    )
    st.session_state.selected_region = selected_region
except Exception as e:
    st.error(f"Error loading regions: {e}")
    selected_region = "All Regions"

# Channel filter
try:
    channels = con.execute("SELECT DISTINCT channel FROM outlets").fetchall()
    channels = [row[0] for row in channels if row[0] is not None]
    channels.sort()  # Sort the channels to ensure consistent order
    channels.insert(0, "All Channels")
    if "selected_channel" not in st.session_state:
        st.session_state.selected_channel = "All Channels"
    selected_channel = st.sidebar.selectbox(
        "Select Channel",
        channels,
        index=channels.index(st.session_state.selected_channel) if st.session_state.selected_channel in channels else 0
    )
    st.session_state.selected_channel = selected_channel
except Exception as e:
    st.error(f"Error loading channels: {e}")
    selected_channel = "All Channels"

# L1 Position filter
try:
    l1_positions = con.execute("SELECT DISTINCT l1_position_name FROM outlets").fetchall()
    l1_positions = [row[0] for row in l1_positions if row[0] is not None]
    l1_positions.sort()  # Sort the L1 positions to ensure consistent order
    l1_positions.insert(0, "All L1 Positions")
    if "selected_l1_position" not in st.session_state:
        st.session_state.selected_l1_position = "All L1 Positions"
    selected_l1_position = st.sidebar.selectbox(
        "Select L1 Position",
        l1_positions,
        index=l1_positions.index(st.session_state.selected_l1_position) if st.session_state.selected_l1_position in l1_positions else 0
    )
    st.session_state.selected_l1_position = selected_l1_position
except Exception as e:
    st.error(f"Error loading L1 positions: {e}")
    selected_l1_position = "All L1 Positions"

# L2 Position filter
try:
    l2_positions = con.execute("SELECT DISTINCT l2_position_name FROM outlets").fetchall()
    l2_positions = [row[0] for row in l2_positions if row[0] is not None]
    l2_positions.sort()  # Sort the L2 positions to ensure consistent order
    l2_positions.insert(0, "All L2 Positions")
    if "selected_l2_position" not in st.session_state:
        st.session_state.selected_l2_position = "All L2 Positions"
    selected_l2_position = st.sidebar.selectbox(
        "Select L2 Position",
        l2_positions,
        index=l2_positions.index(st.session_state.selected_l2_position) if st.session_state.selected_l2_position in l2_positions else 0
    )
    st.session_state.selected_l2_position = selected_l2_position
except Exception as e:
    st.error(f"Error loading L2 positions: {e}")
    selected_l2_position = "All L2 Positions"

# L3 Position filter
try:
    l3_positions = con.execute("SELECT DISTINCT l3_position_name FROM outlets").fetchall()
    l3_positions = [row[0] for row in l3_positions if row[0] is not None]
    l3_positions.sort()  # Sort the L3 positions to ensure consistent order
    l3_positions.insert(0, "All L3 Positions")
    if "selected_l3_position" not in st.session_state:
        st.session_state.selected_l3_position = "All L3 Positions"
    selected_l3_position = st.sidebar.selectbox(
        "Select L3 Position",
        l3_positions,
        index=l3_positions.index(st.session_state.selected_l3_position) if st.session_state.selected_l3_position in l3_positions else 0
    )
    st.session_state.selected_l3_position = selected_l3_position
except Exception as e:
    st.error(f"Error loading L3 positions: {e}")
    selected_l3_position = "All L3 Positions"

# Beat filter
try:
    beats = con.execute("SELECT DISTINCT beat FROM outlets").fetchall()
    beats = [row[0] for row in beats if row[0] is not None]
    beats.sort()  # Sort the beats to ensure consistent order
    beats.insert(0, "All Beats")
    if "selected_beat" not in st.session_state:
        st.session_state.selected_beat = "All Beats"
    selected_beat = st.sidebar.selectbox(
        "Select Beat",
        beats,
        index=beats.index(st.session_state.selected_beat) if st.session_state.selected_beat in beats else 0
    )
    st.session_state.selected_beat = selected_beat
except Exception as e:
    st.error(f"Error loading beats: {e}")
    selected_beat = "All Beats"

# Main dashboard
st.header("Key Performance Indicators")

# KPIs
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

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
    if selected_region != "All Regions":
        outlet_filter_conditions.append(f"o.region = '{selected_region}'")
    if selected_channel != "All Channels":
        outlet_filter_conditions.append(f"o.channel = '{selected_channel}'")
    if selected_l1_position != "All L1 Positions":
        outlet_filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
    if selected_l2_position != "All L2 Positions":
        outlet_filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
    if selected_l3_position != "All L3 Positions":
        outlet_filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
    if selected_beat != "All Beats":
        outlet_filter_conditions.append(f"o.beat = '{selected_beat}'")
    
    if outlet_filter_conditions:
        filtered_outlets_query += " WHERE " + " AND ".join(outlet_filter_conditions)
    
    filtered_outlets = con.execute(filtered_outlets_query).fetchone()[0] or 0
    col7.metric("Filtered Outlets", filtered_outlets)

    # Active outlets (with orders)
    active_outlets_query = """
        SELECT COUNT(DISTINCT o.outlet_id)
        FROM outlets o
        JOIN orders ord ON o.outlet_id = ord.outlet_id
    """
    
    # Add filters
    filter_conditions = []
    if date_range != "All Months":
        filter_conditions.append(f"ord.order_month = '{date_range}'")
    if selected_region != "All Regions":
        filter_conditions.append(f"o.region = '{selected_region}'")
    if selected_channel != "All Channels":
        filter_conditions.append(f"o.channel = '{selected_channel}'")
    if selected_l1_position != "All L1 Positions":
        filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
    if selected_l2_position != "All L2 Positions":
        filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
    if selected_l3_position != "All L3 Positions":
        filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
    if selected_beat != "All Beats":
        filter_conditions.append(f"o.beat = '{selected_beat}'")
    
    if filter_conditions:
        active_outlets_query += " WHERE " + " AND ".join(filter_conditions)
    
    active_outlets = con.execute(active_outlets_query).fetchone()[0] or 0
    col2.metric("Active Outlets", active_outlets)

    # Reordering outlets (with >1 order)
    reordering_query = """
        SELECT COUNT(*)
        FROM (
            SELECT ord.outlet_id
            FROM orders ord
    """
    
    # Add filters
    reordering_conditions = []
    if date_range != "All Months":
        reordering_conditions.append(f"ord.order_month = '{date_range}'")
    if selected_region != "All Regions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
    if selected_channel != "All Channels":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
    if selected_l1_position != "All L1 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
    if selected_l2_position != "All L2 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
    if selected_l3_position != "All L3 Positions":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
    if selected_beat != "All Beats":
        reordering_conditions.append(f"ord.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
    
    if reordering_conditions:
        reordering_query += " WHERE " + " AND ".join(reordering_conditions)
    
    reordering_query += " GROUP BY ord.outlet_id HAVING COUNT(ord.order_id) > 1)"
    
    reordering_outlets = con.execute(reordering_query).fetchone()[0] or 0
    col3.metric("Reordering Outlets", reordering_outlets)

    # Coverage rate
    coverage_rate = 0
    if active_outlets > 0:
        coverage_rate = round((reordering_outlets / active_outlets) * 100, 2)
    col4.metric("Reorder Rate", f"{coverage_rate}%")

    # Visit count
    visit_count_query = """
        SELECT COUNT(*)
        FROM visits v
    """
    
    # Add filters
    visit_filter_conditions = []
    if date_range != "All Months":
        visit_filter_conditions.append(f"v.visit_month = '{date_range}'")
    if selected_region != "All Regions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
    if selected_channel != "All Channels":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
    if selected_l1_position != "All L1 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
    if selected_l2_position != "All L2 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
    if selected_l3_position != "All L3 Positions":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
    if selected_beat != "All Beats":
        visit_filter_conditions.append(f"v.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
    
    if visit_filter_conditions:
        visit_count_query += " WHERE " + " AND ".join(visit_filter_conditions)
    
    visit_count = con.execute(visit_count_query).fetchone()[0] or 0
    col5.metric("Visit Count", visit_count)

    # Unique L1 positions taking orders
    unique_l1_query = """
        SELECT COUNT(DISTINCT o.l1_position_name)
        FROM orders ord
        JOIN outlets o ON ord.outlet_id = o.outlet_id
    """
    
    # Add filters
    l1_filter_conditions = []
    if date_range != "All Months":
        l1_filter_conditions.append(f"ord.order_month = '{date_range}'")
    if selected_region != "All Regions":
        l1_filter_conditions.append(f"o.region = '{selected_region}'")
    if selected_channel != "All Channels":
        l1_filter_conditions.append(f"o.channel = '{selected_channel}'")
    if selected_l1_position != "All L1 Positions":
        l1_filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
    if selected_l2_position != "All L2 Positions":
        l1_filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
    if selected_l3_position != "All L3 Positions":
        l1_filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
    if selected_beat != "All Beats":
        l1_filter_conditions.append(f"o.beat = '{selected_beat}'")
    
    if l1_filter_conditions:
        unique_l1_query += " WHERE " + " AND ".join(l1_filter_conditions)
    
    unique_l1_count = con.execute(unique_l1_query).fetchone()[0] or 0
    col6.metric("Unique L1 Positions", unique_l1_count)
except Exception as e:
    st.error(f"Error calculating KPIs: {e}")

# Tabs for different analysis views
tab1, tab2, tab3, tab4 = st.tabs(["Outlet Performance", "Order Analysis", "Coverage Analysis", "Data Export"])

with tab1:
    st.subheader("Outlet Performance Analysis")
    
    try:
        # Frequency vs Value Scatter Plot
        st.write("Outlet Frequency vs Value Analysis")
        
        # Build filter query for coverage_analysis
        filter_query = ""
        filter_conditions = []
        if selected_region != "All Regions":
            filter_conditions.append(f"o.region = '{selected_region}'")
        if selected_channel != "All Channels":
            filter_conditions.append(f"o.channel = '{selected_channel}'")
        if selected_l1_position != "All L1 Positions":
            filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
        if selected_l2_position != "All L2 Positions":
            filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
        if selected_l3_position != "All L3 Positions":
            filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
        if selected_beat != "All Beats":
            filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        # For date filtering, we need to join with orders table
        if date_range != "All Months":
            # Get outlets that had orders in the selected month
            outlet_filter_query = f"""
                SELECT DISTINCT outlet_id 
                FROM orders 
                WHERE order_month = '{date_range}'
            """
            
            # Add region/channel/L1/L2/L3/beat filters to outlet query if needed
            outlet_filter_conditions = []
            if selected_region != "All Regions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
            if selected_channel != "All Channels":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
            if selected_l1_position != "All L1 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
            if selected_l2_position != "All L2 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
            if selected_l3_position != "All L3 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
            if selected_beat != "All Beats":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
            
            if outlet_filter_conditions:
                outlet_filter_query += " AND " + " AND ".join(outlet_filter_conditions)
            
            filter_conditions.append(f"o.outlet_id IN ({outlet_filter_query})")
        else:
            # If no date filter, still apply region/channel/L1/L2/L3/beat filters
            if selected_region != "All Regions":
                filter_conditions.append(f"o.region = '{selected_region}'")
            if selected_channel != "All Channels":
                filter_conditions.append(f"o.channel = '{selected_channel}'")
            if selected_l1_position != "All L1 Positions":
                filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
            if selected_l2_position != "All L2 Positions":
                filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
            if selected_l3_position != "All L3 Positions":
                filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
            if selected_beat != "All Beats":
                filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        if filter_conditions:
            filter_query = "WHERE " + " AND ".join(filter_conditions)
        
        # Get data for scatter plot
        scatter_data = con.execute(f"""
            SELECT
                ca.outlet_id,
                ca.outlet_name,
                ca.total_orders,
                ca.total_order_value,
                ca.avg_order_value
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
            ORDER BY ca.total_order_value DESC
            LIMIT 1000
        """).fetchdf()
        
        if not scatter_data.empty:
            fig = px.scatter(scatter_data, 
                             x="total_orders", 
                             y="total_order_value", 
                             color="total_orders",
                             hover_data=["outlet_name"],
                             labels={
                                 "total_orders": "Total Orders",
                                 "total_order_value": "Total Order Value"
                             })
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
        
        # Outlet Category Distribution
        st.write("Outlet Category Distribution")
        
        # Categorize outlets based on frequency and value
        # First get the median values
        medians = con.execute(f"""
            SELECT
                MEDIAN(ca.total_orders) as median_orders,
                MEDIAN(ca.total_order_value) as median_value
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
        """).fetchone()
        
        if medians and medians[0] is not None and medians[1] is not None:
            median_orders = medians[0]
            median_value = medians[1]
            
            category_data = con.execute(f"""
                SELECT
                    CASE
                        WHEN ca.total_orders > {median_orders} AND ca.total_order_value > {median_value}
                        THEN 'High Frequency/High Value'
                        WHEN ca.total_orders > {median_orders} AND ca.total_order_value <= {median_value}
                        THEN 'High Frequency/Low Value'
                        WHEN ca.total_orders <= {median_orders} AND ca.total_order_value > {median_value}
                        THEN 'Low Frequency/High Value'
                        ELSE 'Low Frequency/Low Value'
                    END as category,
                    COUNT(*) as count
                FROM coverage_analysis ca
                JOIN outlets o ON ca.outlet_id = o.outlet_id
                {filter_query}
                GROUP BY ALL
            """).fetchdf()
            
            if not category_data.empty:
                fig = px.pie(category_data, values="count", names="category", title="Outlet Category Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No data available for the selected filters.")
        else:
            st.info("No data available for the selected filters.")
    except Exception as e:
        st.error(f"Error in Outlet Performance Analysis: {e}")

with tab2:
    st.subheader("Order Analysis")
    
    try:
        # Top outlets by order value
        st.write("Top Outlets by Order Value")
        
        # Use the same filter query as tab1
        filter_query = ""
        filter_conditions = []
        if selected_region != "All Regions":
            filter_conditions.append(f"o.region = '{selected_region}'")
        if selected_channel != "All Channels":
            filter_conditions.append(f"o.channel = '{selected_channel}'")
        if selected_l1_position != "All L1 Positions":
            filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
        if selected_l2_position != "All L2 Positions":
            filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
        if selected_l3_position != "All L3 Positions":
            filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
        if selected_beat != "All Beats":
            filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        # For date filtering, we need to join with orders table
        if date_range != "All Months":
            # Get outlets that had orders in the selected month
            outlet_filter_query = f"""
                SELECT DISTINCT outlet_id 
                FROM orders 
                WHERE order_month = '{date_range}'
            """
            
            # Add region/channel/L1/L2/L3/beat filters to outlet query if needed
            outlet_filter_conditions = []
            if selected_region != "All Regions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
            if selected_channel != "All Channels":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
            if selected_l1_position != "All L1 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
            if selected_l2_position != "All L2 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
            if selected_l3_position != "All L3 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
            if selected_beat != "All Beats":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
            
            if outlet_filter_conditions:
                outlet_filter_query += " AND " + " AND ".join(outlet_filter_conditions)
            
            filter_conditions.append(f"o.outlet_id IN ({outlet_filter_query})")
        else:
            # If no date filter, still apply region/channel/L1/L2/L3/beat filters
            if selected_region != "All Regions":
                filter_conditions.append(f"o.region = '{selected_region}'")
            if selected_channel != "All Channels":
                filter_conditions.append(f"o.channel = '{selected_channel}'")
            if selected_l1_position != "All L1 Positions":
                filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
            if selected_l2_position != "All L2 Positions":
                filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
            if selected_l3_position != "All L3 Positions":
                filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
            if selected_beat != "All Beats":
                filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        if filter_conditions:
            filter_query = "WHERE " + " AND ".join(filter_conditions)
        
        top_outlets = con.execute(f"""
            SELECT
                ca.outlet_name,
                ca.total_orders,
                ca.total_order_value,
                ca.avg_order_value
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
            ORDER BY ca.total_order_value DESC
            LIMIT 20
        """).fetchdf()
        
        if not top_outlets.empty:
            st.dataframe(top_outlets)
        else:
            st.info("No data available for the selected filters.")
        
        # Order trend over time
        st.write("Order Trend Over Time")
        
        # For trend analysis, we need to use the orders table directly
        # Build a simpler query for the trend analysis
        trend_query = "SELECT order_month, COUNT(order_id) as order_count, SUM(total_amount) as total_value FROM orders ord JOIN outlets o ON ord.outlet_id = o.outlet_id"
        
        # Add filters
        trend_filter_conditions = []
        if selected_region != "All Regions":
            trend_filter_conditions.append(f"o.region = '{selected_region}'")
        if selected_channel != "All Channels":
            trend_filter_conditions.append(f"o.channel = '{selected_channel}'")
        if selected_l1_position != "All L1 Positions":
            trend_filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
        if selected_l2_position != "All L2 Positions":
            trend_filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
        if selected_l3_position != "All L3 Positions":
            trend_filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
        if selected_beat != "All Beats":
            trend_filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        if date_range != "All Months":
            trend_filter_conditions.append(f"ord.order_month = '{date_range}'")
        
        if trend_filter_conditions:
            trend_query += " WHERE " + " AND ".join(trend_filter_conditions)
        
        trend_query += " GROUP BY order_month ORDER BY order_month"
        
        order_trend = con.execute(trend_query).fetchdf()
        
        if not order_trend.empty:
            fig = px.line(order_trend, x="order_month", y="total_value", title="Order Value Trend")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    except Exception as e:
        st.error(f"Error in Order Analysis: {e}")

with tab3:
    st.subheader("Coverage Analysis")
    
    try:
        # Coverage metrics
        st.write("Coverage Metrics")
        
        # Use the same filter query as tab1
        filter_query = ""
        filter_conditions = []
        if selected_region != "All Regions":
            filter_conditions.append(f"o.region = '{selected_region}'")
        if selected_channel != "All Channels":
            filter_conditions.append(f"o.channel = '{selected_channel}'")
        if selected_l1_position != "All L1 Positions":
            filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
        if selected_l2_position != "All L2 Positions":
            filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
        if selected_l3_position != "All L3 Positions":
            filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
        if selected_beat != "All Beats":
            filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        # For date filtering, we need to join with orders table
        if date_range != "All Months":
            # Get outlets that had orders in the selected month
            outlet_filter_query = f"""
                SELECT DISTINCT outlet_id 
                FROM orders 
                WHERE order_month = '{date_range}'
            """
            
            # Add region/channel/L1/L2/L3/beat filters to outlet query if needed
            outlet_filter_conditions = []
            if selected_region != "All Regions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
            if selected_channel != "All Channels":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
            if selected_l1_position != "All L1 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
            if selected_l2_position != "All L2 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
            if selected_l3_position != "All L3 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
            if selected_beat != "All Beats":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
            
            if outlet_filter_conditions:
                outlet_filter_query += " AND " + " AND ".join(outlet_filter_conditions)
            
            filter_conditions.append(f"o.outlet_id IN ({outlet_filter_query})")
        else:
            # If no date filter, still apply region/channel/L1/L2/L3/beat filters
            if selected_region != "All Regions":
                filter_conditions.append(f"o.region = '{selected_region}'")
            if selected_channel != "All Channels":
                filter_conditions.append(f"o.channel = '{selected_channel}'")
            if selected_l1_position != "All L1 Positions":
                filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
            if selected_l2_position != "All L2 Positions":
                filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
            if selected_l3_position != "All L3 Positions":
                filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
            if selected_beat != "All Beats":
                filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        if filter_conditions:
            filter_query = "WHERE " + " AND ".join(filter_conditions)
        
        coverage_metrics = con.execute(f"""
            SELECT
                ca.order_category,
                COUNT(*) as outlet_count,
                AVG(ca.total_visits) as avg_visits
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
            GROUP BY ca.order_category
        """).fetchdf()
        
        if not coverage_metrics.empty:
            st.dataframe(coverage_metrics)
        else:
            st.info("No data available for the selected filters.")
        
        # Visited vs Non-visited Outlets
        st.write("Visited vs Non-visited Outlets")
        
        visit_status = con.execute(f"""
            SELECT
                CASE
                    WHEN ca.total_visits > 0 THEN 'Visited'
                    ELSE 'Not Visited'
                END as visit_status,
                COUNT(*) as outlet_count
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
            GROUP BY ALL
        """).fetchdf()
        
        if not visit_status.empty:
            fig = px.bar(visit_status, x="visit_status", y="outlet_count", title="Visited vs Non-visited Outlets")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
    except Exception as e:
        st.error(f"Error in Coverage Analysis: {e}")

with tab4:
    st.subheader("Data Export")
    
    try:
        # Export filtered data
        st.write("Export Outlet Data")
        
        # Use the same filter query as tab1
        filter_query = ""
        filter_conditions = []
        if selected_region != "All Regions":
            filter_conditions.append(f"o.region = '{selected_region}'")
        if selected_channel != "All Channels":
            filter_conditions.append(f"o.channel = '{selected_channel}'")
        if selected_l1_position != "All L1 Positions":
            filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
        if selected_l2_position != "All L2 Positions":
            filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
        if selected_l3_position != "All L3 Positions":
            filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
        if selected_beat != "All Beats":
            filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        # For date filtering, we need to join with orders table
        if date_range != "All Months":
            # Get outlets that had orders in the selected month
            outlet_filter_query = f"""
                SELECT DISTINCT outlet_id 
                FROM orders 
                WHERE order_month = '{date_range}'
            """
            
            # Add region/channel/L1/L2/L3/beat filters to outlet query if needed
            outlet_filter_conditions = []
            if selected_region != "All Regions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{selected_region}')")
            if selected_channel != "All Channels":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{selected_channel}')")
            if selected_l1_position != "All L1 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{selected_l1_position}')")
            if selected_l2_position != "All L2 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{selected_l2_position}')")
            if selected_l3_position != "All L3 Positions":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{selected_l3_position}')")
            if selected_beat != "All Beats":
                outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{selected_beat}')")
            
            if outlet_filter_conditions:
                outlet_filter_query += " AND " + " AND ".join(outlet_filter_conditions)
            
            filter_conditions.append(f"o.outlet_id IN ({outlet_filter_query})")
        else:
            # If no date filter, still apply region/channel/L1/L2/L3/beat filters
            if selected_region != "All Regions":
                filter_conditions.append(f"o.region = '{selected_region}'")
            if selected_channel != "All Channels":
                filter_conditions.append(f"o.channel = '{selected_channel}'")
            if selected_l1_position != "All L1 Positions":
                filter_conditions.append(f"o.l1_position_name = '{selected_l1_position}'")
            if selected_l2_position != "All L2 Positions":
                filter_conditions.append(f"o.l2_position_name = '{selected_l2_position}'")
            if selected_l3_position != "All L3 Positions":
                filter_conditions.append(f"o.l3_position_name = '{selected_l3_position}'")
            if selected_beat != "All Beats":
                filter_conditions.append(f"o.beat = '{selected_beat}'")
        
        if filter_conditions:
            filter_query = "WHERE " + " AND ".join(filter_conditions)
        
        export_data = con.execute(f"""
            SELECT
                ca.outlet_id,
                ca.outlet_name,
                o.outlet_creation_date,
                ca.region,
                ca.state,
                ca.city,
                ca.channel,
                ca.outlet_type,
                ca.l1_position_name,
                ca.l2_position_name,
                ca.l3_position_name,
                ca.beat,
                ca.total_orders,
                ca.total_order_value,
                ca.avg_order_value,
                ca.first_order_date,
                ca.last_order_date,
                ca.order_category,
                ca.total_visits
            FROM coverage_analysis ca
            JOIN outlets o ON ca.outlet_id = o.outlet_id
            {filter_query}
        """).fetchdf()
        
        if not export_data.empty:
            st.download_button(
                label="Download CSV",
                data=export_data.to_csv(index=False),
                file_name="outlet_performance_data.csv",
                mime="text/csv"
            )
            
            st.dataframe(export_data)
        else:
            st.info("No data available for the selected filters.")
    except Exception as e:
        st.error(f"Error in Data Export: {e}")

# Note: We're not closing the connection here because it's managed by the cache decorator
# The connection will be closed when the Streamlit app shuts down