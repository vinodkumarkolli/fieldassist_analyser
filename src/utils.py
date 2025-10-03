import streamlit as st
import duckdb
from config import DATABASE_PATH

def get_database_connection():
    """Get a cached connection to the DuckDB database."""
    @st.cache_resource
    def connect():
        return duckdb.connect(DATABASE_PATH)
    return connect()

def initialize_filters():
    """Initialize sidebar filters with session state persistence."""
    st.sidebar.header("Filters")
    
    # Date range filter
    if "date_range" not in st.session_state:
        st.session_state.date_range = "All Months"
    date_range_options = ["All Months", "01-25", "02-25", "03-25", "04-25", "05-25", "06-25", "07-25", "08-25", "09-25"]
    date_range = st.sidebar.selectbox(
        "Select Month Range",
        date_range_options,
        index=date_range_options.index(st.session_state.date_range) if st.session_state.date_range in date_range_options else 0
    )
    st.session_state.date_range = date_range

    # Region filter
    con = get_database_connection()
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
        st.session_state.selected_region = "All Regions"

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
        st.session_state.selected_channel = "All Channels"

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
        st.session_state.selected_l1_position = "All L1 Positions"

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
        st.session_state.selected_l2_position = "All L2 Positions"

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
        st.session_state.selected_l3_position = "All L3 Positions"

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
        st.session_state.selected_beat = "All Beats"

def build_filter_query():
    """Build a filter query string based on session state filters."""
    filter_conditions = []
    if st.session_state.date_range != "All Months":
        # For date filtering, we need to join with orders table
        outlet_filter_query = f"""
            SELECT DISTINCT outlet_id 
            FROM orders 
            WHERE order_month = '{st.session_state.date_range}'
        """
        
        # Add region/channel/L1/L2/L3/beat filters to outlet query if needed
        outlet_filter_conditions = []
        if st.session_state.selected_region != "All Regions":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE region = '{st.session_state.selected_region}')")
        if st.session_state.selected_channel != "All Channels":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE channel = '{st.session_state.selected_channel}')")
        if st.session_state.selected_l1_position != "All L1 Positions":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l1_position_name = '{st.session_state.selected_l1_position}')")
        if st.session_state.selected_l2_position != "All L2 Positions":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l2_position_name = '{st.session_state.selected_l2_position}')")
        if st.session_state.selected_l3_position != "All L3 Positions":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE l3_position_name = '{st.session_state.selected_l3_position}')")
        if st.session_state.selected_beat != "All Beats":
            outlet_filter_conditions.append(f"o.outlet_id IN (SELECT outlet_id FROM outlets WHERE beat = '{st.session_state.selected_beat}')")
        
        if outlet_filter_conditions:
            outlet_filter_query += " AND " + " AND ".join(outlet_filter_conditions)
        
        filter_conditions.append(f"o.outlet_id IN ({outlet_filter_query})")
    else:
        # If no date filter, still apply region/channel/L1/L2/L3/beat filters
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
    
    filter_query = ""
    if filter_conditions:
        filter_query = "WHERE " + " AND ".join(filter_conditions)
    
    return filter_query