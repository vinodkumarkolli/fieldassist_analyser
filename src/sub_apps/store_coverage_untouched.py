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
        st.write("**TM (This Month)**: Stores with no visits in the current selected month.")
        st.write("**LM (Last Month)**: Stores with no orders in the last month relative to the selected month.")
        st.write("**L3M (Last 3 Months)**: Stores with no orders in the last 3 months relative to the selected month.")
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            # Calculate untouched stores for TM (This Month) - Stores with no visits in the selected month
            # Build the WHERE clause properly by combining filter conditions
            if filter_query.strip():
                # filter_query already starts with WHERE, so we need to combine it properly
                tm_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN visits v ON o.outlet_id = v.outlet_id AND v.visit_month = '{selected_month}'
                    {filter_query}
                    AND v.outlet_id IS NULL AND o.is_blocked = 'No'
                """
            else:
                tm_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN visits v ON o.outlet_id = v.outlet_id AND v.visit_month = '{selected_month}'
                    WHERE v.outlet_id IS NULL AND o.is_blocked = 'No'
                """
            tm_count = con.execute(tm_query).fetchone()[0] or 0
            
            # Alternative query to debug date format issue
            sample_visit_month_query = """
                SELECT DISTINCT visit_month
                FROM visits
                LIMIT 1
            """
            sample_visit_month = con.execute(sample_visit_month_query).fetchone()
            sample_text = f"Sample visit_month format: {sample_visit_month[0] if sample_visit_month else 'No data'}"
            st.text(sample_text)
            
            # Debug metrics for verification
            # First, count without filters to see total non-blocked outlets
            total_non_blocked_query = """
                SELECT COUNT(DISTINCT o.outlet_id) as total_non_blocked_count
                FROM outlets o
                WHERE o.is_blocked = 'No'
            """
            total_non_blocked_count = con.execute(total_non_blocked_query).fetchone()[0] or 0
            
            # Then apply filters
            non_blocked_query = f"""
                SELECT COUNT(DISTINCT o.outlet_id) as non_blocked_count
                FROM outlets o
                {filter_query}
                {'AND' if filter_query.strip() else 'WHERE'} o.is_blocked = 'No'
            """
            non_blocked_count = con.execute(non_blocked_query).fetchone()[0] or 0
            
            visited_query = f"""
                SELECT COUNT(DISTINCT v.outlet_id) as visited_count
                FROM visits v
                WHERE v.visit_month = '{selected_month}'
            """
            if filter_query.strip():
                visited_query += f" AND v.outlet_id IN (SELECT outlet_id FROM outlets o {filter_query})"
            visited_count = con.execute(visited_query).fetchone()[0] or 0
            
            # Additional debug to check if any visits exist for the selected month
            total_visits_query = f"""
                SELECT COUNT(*) as total_visits
                FROM visits v
                WHERE v.visit_month = '{selected_month}'
            """
            total_visits = con.execute(total_visits_query).fetchone()[0] or 0
            
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Untouched Stores - This Month (TM)", tm_count)
            col2.metric("Non-Blocked Outlets (Filtered)", non_blocked_count)
            col3.metric("Non-Blocked Outlets (Total)", total_non_blocked_count)
            col4.metric("Unique Visited Outlets (Debug)", visited_count)
            col5.metric("Total Visits (Debug)", total_visits)
            
            # Calculate untouched stores for LM (Last Month)
            # Assuming months are in format MM-YY, calculate the previous month
            month, year = map(int, selected_month.split('-'))
            if month == 1:
                lm_month = f"12-{year-1:02d}"
            else:
                lm_month = f"{month-1:02d}-{year:02d}"
            # Build the WHERE clause properly for LM query
            if filter_query.strip():
                # filter_query already starts with WHERE, so we need to combine it properly
                lm_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month = '{lm_month}'
                    {filter_query}
                    AND ord.outlet_id IS NULL AND o.is_blocked = 'No'
                """
            else:
                lm_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month = '{lm_month}'
                    WHERE ord.outlet_id IS NULL AND o.is_blocked = 'No'
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
            # Build the WHERE clause properly for L3M query
            if filter_query.strip():
                # filter_query already starts with WHERE, so we need to combine it properly
                l3m_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month IN ('{l3m_months_str}')
                    {filter_query}
                    AND ord.outlet_id IS NULL AND o.is_blocked = 'No'
                """
            else:
                l3m_query = f"""
                    SELECT COUNT(DISTINCT o.outlet_id) as untouched_count
                    FROM outlets o
                    LEFT JOIN orders ord ON o.outlet_id = ord.outlet_id AND ord.order_month IN ('{l3m_months_str}')
                    WHERE ord.outlet_id IS NULL AND o.is_blocked = 'No'
                """
            l3m_count = con.execute(l3m_query).fetchone()[0] or 0
            st.metric("Untouched Stores - Last 3 Months (L3M)", l3m_count)
            
            # Breakdown by region for TM
            st.write("Untouched Stores (TM) Breakdown by Region")

            if filter_query.strip():
                # filter_query already starts with WHERE, so we need to combine it properly
                tm_region_query = f"""
                    SELECT
                        o.region,
                        COUNT(DISTINCT o.outlet_id) as untouched_count,
                        COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
                    FROM outlets o
                    LEFT JOIN visits v ON o.outlet_id = v.outlet_id AND v.visit_month = '{selected_month}'
                    {filter_query}
                    AND v.outlet_id IS NULL AND o.is_blocked = 'No'
                    GROUP BY o.region
                    ORDER BY untouched_count DESC
                """
            else:
                tm_region_query = f"""
                    SELECT
                        o.region,
                        COUNT(DISTINCT o.outlet_id) as untouched_count,
                        COUNT(DISTINCT o.outlet_id) * 100.0 / SUM(COUNT(DISTINCT o.outlet_id)) OVER () as percentage
                    FROM outlets o
                    LEFT JOIN visits v ON o.outlet_id = v.outlet_id AND v.visit_month = '{selected_month}'
                    WHERE v.outlet_id IS NULL AND o.is_blocked = 'No'
                    GROUP BY o.region
                    ORDER BY untouched_count DESC
                """

            tm_region_breakdown = con.execute(tm_region_query).fetchdf()
            
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
        # Do not close the connection here to avoid "Connection already closed" errors
        # The connection is managed by Streamlit's cache_resource decorator in utils.py
        pass

if __name__ == "__main__":
    app()