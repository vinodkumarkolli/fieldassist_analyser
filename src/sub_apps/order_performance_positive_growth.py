import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Order Performance - PCs with Positive Growth")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        if st.session_state.date_range != "All Months":
            selected_month = st.session_state.date_range
            # Calculate PCs with positive growth compared to last month
            month, year = map(int, selected_month.split('-'))
            if month == 1:
                lm_month = f"12-{year-1:02d}"
            else:
                lm_month = f"{month-1:02d}-{year:02d}"
                
            growth_query = f"""
                WITH CurrentMonth AS (
                    SELECT 
                        o.outlet_id,
                        o.outlet_name,
                        o.region,
                        SUM(ord.total_amount) as current_value
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{selected_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                    GROUP BY o.outlet_id, o.outlet_name, o.region
                ),
                LastMonth AS (
                    SELECT 
                        o.outlet_id,
                        SUM(ord.total_amount) as last_value
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{lm_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                    GROUP BY o.outlet_id
                ),
                Growth AS (
                    SELECT 
                        cm.outlet_id,
                        cm.outlet_name,
                        cm.region,
                        cm.current_value,
                        lm.last_value,
                        CASE 
                            WHEN lm.last_value > 0 
                            THEN ((cm.current_value - lm.last_value) / lm.last_value) * 100
                            ELSE 100.0
                        END as growth_percentage
                    FROM CurrentMonth cm
                    LEFT JOIN LastMonth lm ON cm.outlet_id = lm.outlet_id
                    WHERE cm.current_value > 0
                )
                SELECT 
                    outlet_id,
                    outlet_name,
                    region,
                    current_value,
                    last_value,
                    growth_percentage
                FROM Growth
                WHERE growth_percentage > 0
                ORDER BY growth_percentage DESC
                LIMIT 20
            """
            growth_data = con.execute(growth_query).fetchdf()
            
            if not growth_data.empty:
                st.write(f"Top 20 Outlets with Positive Growth (compared to {lm_month})")
                st.dataframe(growth_data)
                fig = px.bar(growth_data, x="outlet_name", y="growth_percentage", color="region", 
                             title="Outlets with Positive Growth Compared to Last Month (%)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No outlets with positive growth for the selected period.")
                
            # Average growth compared to overall average
            avg_growth_query = f"""
                WITH CurrentMonth AS (
                    SELECT 
                        o.outlet_id,
                        o.outlet_name,
                        o.region,
                        SUM(ord.total_amount) as current_value
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month = '{selected_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                    GROUP BY o.outlet_id, o.outlet_name, o.region
                ),
                OverallAvg AS (
                    SELECT 
                        o.outlet_id,
                        AVG(ord.total_amount) as avg_value
                    FROM orders ord
                    JOIN outlets o ON ord.outlet_id = o.outlet_id
                    WHERE ord.order_month != '{selected_month}'
                    AND {filter_query.split('WHERE ')[1] if 'WHERE' in filter_query else '1=1'}
                    GROUP BY o.outlet_id
                    HAVING COUNT(DISTINCT ord.order_month) > 0
                ),
                Growth AS (
                    SELECT 
                        cm.outlet_id,
                        cm.outlet_name,
                        cm.region,
                        cm.current_value,
                        oa.avg_value,
                        CASE 
                            WHEN oa.avg_value > 0 
                            THEN ((cm.current_value - oa.avg_value) / oa.avg_value) * 100
                            ELSE 100.0
                        END as growth_percentage
                    FROM CurrentMonth cm
                    LEFT JOIN OverallAvg oa ON cm.outlet_id = oa.outlet_id
                    WHERE cm.current_value > 0
                )
                SELECT 
                    outlet_id,
                    outlet_name,
                    region,
                    current_value,
                    avg_value,
                    growth_percentage
                FROM Growth
                WHERE growth_percentage > 0
                ORDER BY growth_percentage DESC
                LIMIT 20
            """
            avg_growth_data = con.execute(avg_growth_query).fetchdf()
            
            if not avg_growth_data.empty:
                st.write("Top 20 Outlets with Positive Growth (compared to historical average)")
                st.dataframe(avg_growth_data)
                fig_avg = px.bar(avg_growth_data, x="outlet_name", y="growth_percentage", color="region", 
                                 title="Outlets with Positive Growth Compared to Historical Average (%)")
                st.plotly_chart(fig_avg, use_container_width=True)
            else:
                st.info("No outlets with positive growth compared to historical average.")
        else:
            st.warning("Please select a specific month to view Positive Growth data.")
            
    except Exception as e:
        st.error(f"Error in Order Performance - Positive Growth PCs: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()