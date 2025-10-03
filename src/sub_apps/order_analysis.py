import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH

def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

def app():
    st.subheader("Order Analysis")
    
    con = get_database_connection()
    
    try:
        # Top outlets by order value
        st.write("Top Outlets by Order Value")
        
        # Use the same filter query as tab1
        filter_query = ""
        filter_conditions = []
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
        
        # For date filtering, we need to join with orders table
        if st.session_state.date_range != "All Months":
            # Get outlets that had orders in the selected month
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
        if st.session_state.selected_region != "All Regions":
            trend_filter_conditions.append(f"o.region = '{st.session_state.selected_region}'")
        if st.session_state.selected_channel != "All Channels":
            trend_filter_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
        if st.session_state.selected_l1_position != "All L1 Positions":
            trend_filter_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
        if st.session_state.selected_l2_position != "All L2 Positions":
            trend_filter_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
        if st.session_state.selected_l3_position != "All L3 Positions":
            trend_filter_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
        if st.session_state.selected_beat != "All Beats":
            trend_filter_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
        
        if st.session_state.date_range != "All Months":
            trend_filter_conditions.append(f"ord.order_month = '{st.session_state.date_range}'")
        
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
    finally:
        con.close()

if __name__ == "__main__":
    app()