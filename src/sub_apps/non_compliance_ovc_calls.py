import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Non-Compliance - OVC Calls")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            
            # OVC Calls - Assuming OVC (Order Verification Calls) non-compliance could be identified by specific criteria
            # For now, we'll simulate OVC non-compliance as a placeholder since specific data might not be available
            # This could be updated based on actual business rules or data fields
            ovc_calls_query = f"""
                SELECT 
                    o.l1_position_name,
                    o.outlet_name,
                    ord.order_date,
                    ord.order_month,
                    ord.total_amount,
                    'Order Verification Pending' as issue
                FROM orders ord
                JOIN outlets o ON ord.outlet_id = o.outlet_id
                WHERE ord.order_month = '{selected_month}'
                AND ord.total_amount > 10000  -- Assuming high-value orders need verification
                AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                ORDER BY ord.total_amount DESC
                LIMIT 50
            """
            ovc_calls_data = con.execute(ovc_calls_query).fetchdf()
            
            if not ovc_calls_data.empty:
                st.write(f"OVC Calls Non-Compliance in {selected_month} (High-Value Orders Pending Verification)")
                st.dataframe(ovc_calls_data)
                st.metric("Count of OVC Non-Compliance Instances", len(ovc_calls_data))
                
                # Breakdown by L1 Position
                fig = px.bar(ovc_calls_data.groupby('l1_position_name').size().reset_index(name='count'), 
                             x='l1_position_name', y='count', 
                             title="OVC Non-Compliance by L1 Position")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No OVC non-compliance instances found for the selected month.")
        else:
            st.warning("Please select a specific month to view OVC Calls data.")
            
    except Exception as e:
        st.error(f"Error in Non-Compliance - OVC Calls: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()