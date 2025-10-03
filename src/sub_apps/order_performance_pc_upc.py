import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Order Performance - PC & UPC (Unique)")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        # PC (Productive Calls) - Unique outlets with orders
        pc_query = f"""
            SELECT COUNT(DISTINCT o.outlet_id) as pc_count
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
        """
        pc_count = con.execute(pc_query).fetchone()[0] or 0
        st.metric("Productive Calls (PC) - Unique Outlets with Orders", pc_count)
        
        # UPC (Unique Productive Calls) - Unique outlets with orders in the selected period
        upc_query = f"""
            SELECT COUNT(DISTINCT o.outlet_id) as upc_count
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
        """
        if st.session_state.date_range != "All Months":
            upc_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as upc_count
                FROM outlets o
                JOIN orders ord ON o.outlet_id = ord.outlet_id
                WHERE ord.order_month = '{st.session_state.date_range}'
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
            """
        upc_count = con.execute(upc_query).fetchone()[0] or 0
        st.metric("Unique Productive Calls (UPC) - Unique Outlets with Orders in Period", upc_count)
        
        # Breakdown by region or other dimensions if needed
        st.write("PC Breakdown by Region")
        pc_region_breakdown = con.execute(f"""
            SELECT 
                o.region,
                COUNT(DISTINCT o.outlet_id) as pc_count,
                COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
            GROUP BY o.region
            ORDER BY pc_count DESC
        """).fetchdf()
        
        if not pc_region_breakdown.empty:
            st.dataframe(pc_region_breakdown)
            fig = px.pie(pc_region_breakdown, values="pc_count", names="region", title="PC Distribution by Region")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
            
        if st.session_state.date_range != "All Months":
            st.write("UPC Breakdown by Region")
            upc_region_breakdown = con.execute(f"""
                SELECT 
                    o.region,
                    COUNT(DISTINCT o.outlet_id) as upc_count,
                    COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
                FROM outlets o
                JOIN orders ord ON o.outlet_id = ord.outlet_id
                WHERE ord.order_month = '{st.session_state.date_range}'
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                GROUP BY o.region
                ORDER BY upc_count DESC
            """).fetchdf()
            
            if not upc_region_breakdown.empty:
                st.dataframe(upc_region_breakdown)
                fig_upc = px.pie(upc_region_breakdown, values="upc_count", names="region", title="UPC Distribution by Region")
                st.plotly_chart(fig_upc, use_container_width=True)
            else:
                st.info("No UPC data available for the selected period.")
                
    except Exception as e:
        st.error(f"Error in Order Performance - PC & UPC: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()