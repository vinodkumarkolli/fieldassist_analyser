import streamlit as st
import duckdb
from config import DATABASE_PATH

def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

def app():
    st.subheader("Data Export")
    
    con = get_database_connection()
    
    try:
        # Export filtered data
        st.write("Export Outlet Data")
        
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
    finally:
        con.close()

if __name__ == "__main__":
    app()