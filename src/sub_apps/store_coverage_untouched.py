import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Store Coverage - Untouched Stores (TM, LM, L3M)")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        # Explanation of time periods
        st.write("**TM (This Month)**: Stores with no orders in the current selected month.")
        st.write("**LM (Last Month)**: Stores with no orders in the last month relative to the selected month.")
        st.write("**L3M (Last 3 Months)**: Stores with no orders in the last 3 months relative to the selected month.")
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            # Calculate untouched stores for TM (This Month)
            tm_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                FROM outlets o
                LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month = '{selected_month}'
                {filter_query}
                WHERE ord.outlet_id IS NULL
            """
            tm_count = con.execute(tm_query).fetchone()[0] or 0
            st.metric("Untouched Stores - This Month (TM)", tm_count)
            
            # Calculate untouched stores for LM (Last Month)
            # Assuming months are in format MM-YY, calculate the previous month
            month, year = map(int, selected_month.split('-'))
            if month == 1:
                lm_month = f"12-{year-1:02d}"
            else:
                lm_month = f"{month-1:02d}-{year:02d}"
            lm_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                FROM outlets o
                LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month = '{lm_month}'
                {filter_query}
                WHERE ord.outlet_id IS NULL
            """
            lm_count = con.execute(lm_query).fetchone()[0] or 0
            st.metric("Untouched Stores - Last Month (LM)", lm_count)
            
            # Calculate untouched stores for L3M (Last 3 Months)
            # Calculate the last 3 months range
            l3m_months = []
            for i in range(1, 4):
                if month - i <= 0:
                    adj_month = 12 + (month - i)
                    adj_year = year - 1
                else:
                    adj_month = month - i
                    adj_year = year
                l3m_months.append(f"{adj_month:02d}-{adj_year:02d}")
            l3m_months_str = "', '".join(l3m_months)
            l3m_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                FROM outlets o
                LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month IN ('{l3m_months_str}')
                {filter_query}
                WHERE ord.outlet_id IS NULL
            """
            l3m_count = con.execute(l3m_query).fetchone()[0] or 0
            st.metric("Untouched Stores - Last 3 Months (L3M)", l3m_count)
            
            # Breakdown by region for TM
            st.write("Untouched Stores (TM) Breakdown by Region")
            tm_region_breakdown = con.execute(f"""
                SELECT 
                    o.region,
                    COUNT(DISTINCT o.outlet_id) as untouched_count,
                    COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
                FROM outlets o
                LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month = '{selected_month}'
                {filter_query}
                WHERE ord.outlet_id IS NULL
                GROUP BY o.region
                ORDER BY untouched_count DESC
            """).fetchdf()
            
            if not tm_region_breakdown.empty:
                st.dataframe(tm_region_breakdown)
                fig_tm = px.pie(tm_region_breakdown, values="untouched_count", names="region", title="Untouched Stores (TM) Distribution by Region")
                st.plotly_chart(fig_tm, use_container_width=True)
            else:
                st.info("No data available for untouched stores this month.")
                
        else:
            st.warning("Please select a specific month to view Untouched Stores data for TM, LM, and L3M.")
            
    except Exception as e:
        st.error(f"Error in Store Coverage - Untouched Stores: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()