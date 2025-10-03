import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH

def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

def app():
    st.subheader("Outlet Performance Analysis")
    
    con = get_database_connection()
    
    try:
        # Order Performance KPIs
        st.write("Order Performance KPIs")
        col1,col2 = st.columns(2)
        # Total Order Value
        total_order_value_query = """
            SELECT SUM(ord.total_amount) as total_value
            FROM orders ord
            JOIN outlets o ON ord.outlet_id = o.outlet_id
        """
        
        # Add filters
        order_filter_conditions = []
        if st.session_state.date_range != "All Months":
            order_filter_conditions.append(f"ord.order_month = '{st.session_state.date_range}'")
        if st.session_state.selected_region != "All Regions":
            order_filter_conditions.append(f"o.region = '{st.session_state.selected_region}'")
        if st.session_state.selected_channel != "All Channels":
            order_filter_conditions.append(f"o.channel = '{st.session_state.selected_channel}'")
        if st.session_state.selected_l1_position != "All L1 Positions":
            order_filter_conditions.append(f"o.l1_position_name = '{st.session_state.selected_l1_position}'")
        if st.session_state.selected_l2_position != "All L2 Positions":
            order_filter_conditions.append(f"o.l2_position_name = '{st.session_state.selected_l2_position}'")
        if st.session_state.selected_l3_position != "All L3 Positions":
            order_filter_conditions.append(f"o.l3_position_name = '{st.session_state.selected_l3_position}'")
        if st.session_state.selected_beat != "All Beats":
            order_filter_conditions.append(f"o.beat = '{st.session_state.selected_beat}'")
        
        if order_filter_conditions:
            total_order_value_query += " WHERE " + " AND ".join(order_filter_conditions)
        
        total_order_value = con.execute(total_order_value_query).fetchone()[0] or 0
        col1.metric("Total Order Value", f"{total_order_value:,.2f}")
    
        # Average Order Value
        avg_order_value_query = """
            SELECT AVG(ord.total_amount) as avg_value
            FROM orders ord
            JOIN outlets o ON ord.outlet_id = o.outlet_id
        """
        
        if order_filter_conditions:
            avg_order_value_query += " WHERE " + " AND ".join(order_filter_conditions)
        
        avg_order_value = con.execute(avg_order_value_query).fetchone()[0] or 0
        col2.metric("Average Order Value", f"{avg_order_value:,.2f}")
    
        # Frequency vs Value Scatter Plot
        st.write("Outlet Frequency vs Value Analysis")
        
        # Build filter query for coverage_analysis
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
    finally:
        con.close()

if __name__ == "__main__":
    app()