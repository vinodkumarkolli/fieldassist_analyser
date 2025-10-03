import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH

def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

def app():
    st.subheader("Coverage Analysis")
    
    con = get_database_connection()
    
    try:
        # Coverage metrics
        st.write("Coverage Metrics")
        
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
    finally:
        con.close()

if __name__ == "__main__":
    app()