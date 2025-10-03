import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Order Performance - TCs Stopped Ordering (LM, L3M)")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            # Calculate TCs that stopped ordering in LM (Last Month)
            month, year = map(int, selected_month.split('-'))
            if month == 1:
                lm_month = f"12-{year-1:02d}"
            else:
                lm_month = f"{month-1:02d}-{year:02d}"
                
            lm_stopped_query = f"""
                WITH LastMonthActive AS (
                    SELECT DISTINCT o.l1_position_name
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{lm_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                ),
                CurrentMonthActive AS (
                    SELECT DISTINCT o.l1_position_name
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{selected_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                )
                SELECT lma.l1_position_name
                FROM LastMonthActive lma
                LEFT JOIN CurrentMonthActive cma ON lma.l1_position_name = cma.l1_position_name
                WHERE cma.l1_position_name IS NULL
                ORDER BY lma.l1_position_name
            """
            lm_stopped_data = con.execute(lm_stopped_query).fetchdf()
            
            if not lm_stopped_data.empty:
                st.write(f"TCs Stopped Ordering in Current Month (compared to {lm_month})")
                st.dataframe(lm_stopped_data)
                st.metric("Count of TCs Stopped Ordering (LM)", len(lm_stopped_data))
            else:
                st.info("No TCs stopped ordering in the current month compared to last month.")
            
            # Calculate TCs that stopped ordering in L3M (Last 3 Months)
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
            
            l3m_stopped_query = f"""
                WITH LastThreeMonthsActive AS (
                    SELECT DISTINCT o.l1_position_name
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month IN ('{l3m_months_str}')
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                ),
                CurrentMonthActive AS (
                    SELECT DISTINCT o.l1_position_name
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{selected_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                )
                SELECT ltma.l1_position_name
                FROM LastThreeMonthsActive ltma
                LEFT JOIN CurrentMonthActive cma ON ltma.l1_position_name = cma.l1_position_name
                WHERE cma.l1_position_name IS NULL
                ORDER BY ltma.l1_position_name
            """
            l3m_stopped_data = con.execute(l3m_stopped_query).fetchdf()
            
            if not l3m_stopped_data.empty:
                st.write("TCs Stopped Ordering in Current Month (compared to last 3 months)")
                st.dataframe(l3m_stopped_data)
                st.metric("Count of TCs Stopped Ordering (L3M)", len(l3m_stopped_data))
            else:
                st.info("No TCs stopped ordering in the current month compared to the last 3 months.")
        else:
            st.warning("Please select a specific month to view Stopped Ordering data for LM and L3M.")
            
    except Exception as e:
        st.error(f"Error in Order Performance - Stopped Ordering TCs: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()