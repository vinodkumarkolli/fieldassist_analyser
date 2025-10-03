import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Non-Compliance - Late Reporting")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            
            # Late Reporting - Assuming late reporting could be identified by visit or order timestamps
            # For now, we'll simulate late reporting as visits/orders reported after a certain day of the month
            # This is a placeholder logic; actual logic would depend on specific business rules
            late_reporting_query = f"""
                SELECT 
                    o.l1_position_name,
                    o.outlet_name,
                    v.visit_date,
                    v.visit_month,
                    'Visit' as report_type
                FROM visits v
                JOIN outlets o ON v.outlet_id = o.outlet_id
                WHERE v.visit_month = '{selected_month}'
                AND EXTRACT(DAY FROM v.visit_date) > 15  -- Assuming late if reported after 15th
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                UNION ALL
                SELECT 
                    o.l1_position_name,
                    o.outlet_name,
                    ord.order_date as visit_date,
                    ord.order_month as visit_month,
                    'Order' as report_type
                FROM orders ord
                JOIN outlets o ON ord.outlet_id = o.outlet_id
                WHERE ord.order_month = '{selected_month}'
                AND EXTRACT(DAY FROM ord.order_date) > 15  -- Assuming late if reported after 15th
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                ORDER BY visit_date DESC
                LIMIT 50
            """
            late_reporting_data = con.execute(late_reporting_query).fetchdf()
            
            if not late_reporting_data.empty:
                st.write(f"Late Reporting Instances in {selected_month} (after 15th of the month)")
                st.dataframe(late_reporting_data)
                st.metric("Count of Late Reporting Instances", len(late_reporting_data))
                
                # Breakdown by L1 Position
                fig = px.bar(late_reporting_data.groupby('l1_position_name').size().reset_index(name='count'), 
                             x='l1_position_name', y='count', 
                             title="Late Reporting by L1 Position")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No late reporting instances found for the selected month.")
        else:
            st.warning("Please select a specific month to view Late Reporting data.")
            
    except Exception as e:
        st.error(f"Error in Non-Compliance - Late Reporting: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()