import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Store Coverage - Universe")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        # Total universe of stores
        total_universe_query = f"""
            SELECT COUNT(*) as total_stores
            FROM outlets o
            {filter_query}
        """
        total_universe = con.execute(total_universe_query).fetchone()[0] or 0
        st.metric("Total Universe of Stores", total_universe)
        
        # Breakdown by region or other dimensions if needed
        st.write("Breakdown by Region")
        region_breakdown = con.execute(f"""
            SELECT 
                o.region,
                COUNT(*) as store_count,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
            FROM outlets o
            {filter_query}
            GROUP BY o.region
            ORDER BY store_count DESC
        """).fetchdf()
        
        if not region_breakdown.empty:
            st.dataframe(region_breakdown)
            fig = px.pie(region_breakdown, values="store_count", names="region", title="Store Distribution by Region")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
            
    except Exception as e:
        st.error(f"Error in Store Coverage - Universe: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()