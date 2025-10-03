import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Store Coverage - TC & UTC (Unique)")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        # TC (Total Coverage) - Unique outlets with at least one order
        tc_query = f"""
            SELECT COUNT(DISTINCT o.outlet_id) as tc_count
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
        """
        tc_count = con.execute(tc_query).fetchone()[0] or 0
        st.metric("Total Coverage (TC) - Unique Outlets with Orders", tc_count)
        
        # UTC (Unique Transaction Coverage) - Unique outlets with orders in the selected period
        utc_query = f"""
            SELECT COUNT(DISTINCT o.outlet_id) as utc_count
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
        """
        if st.session_state.date_range != "All Months":
            utc_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as utc_count
                FROM outlets o
                JOIN orders ord ON o.outlet_id = ord.outlet_id
                WHERE ord.order_month = '{st.session_state.date_range}'
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
            """
        utc_count = con.execute(utc_query).fetchone()[0] or 0
        st.metric("Unique Transaction Coverage (UTC) - Unique Outlets with Orders in Period", utc_count)
        
        # Breakdown by region or other dimensions if needed
        st.write("TC Breakdown by Region")
        tc_region_breakdown = con.execute(f"""
            SELECT 
                o.region,
                COUNT(DISTINCT o.outlet_id) as tc_count,
                COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
            FROM outlets o
            JOIN orders ord ON o.outlet_id = ord.outlet_id
            {filter_query}
            GROUP BY o.region
            ORDER BY tc_count DESC
        """).fetchdf()
        
        if not tc_region_breakdown.empty:
            st.dataframe(tc_region_breakdown)
            fig = px.pie(tc_region_breakdown, values="tc_count", names="region", title="TC Distribution by Region")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
            
        if st.session_state.date_range != "All Months":
            st.write("UTC Breakdown by Region")
            utc_region_breakdown = con.execute(f"""
                SELECT 
                    o.region,
                    COUNT(DISTINCT o.outlet_id) as utc_count,
                    COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
                FROM outlets o
                JOIN orders ord ON o.outlet_id = ord.outlet_id
                WHERE ord.order_month = '{st.session_state.date_range}'
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                GROUP BY o.region
                ORDER BY utc_count DESC
            """).fetchdf()
            
            if not utc_region_breakdown.empty:
                st.dataframe(utc_region_breakdown)
                fig_utc = px.pie(utc_region_breakdown, values="utc_count", names="region", title="UTC Distribution by Region")
                st.plotly_chart(fig_utc, use_container_width=True)
            else:
                st.info("No UTC data available for the selected period.")
                
    except Exception as e:
        st.error(f"Error in Store Coverage - TC & UTC: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()