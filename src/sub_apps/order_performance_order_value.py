import streamlit as st
import duckdb
import plotly.express as px
from config import DATABASE_PATH
from utils import build_filter_query, get_database_connection

def app():
    st.subheader("Order Performance - Order Value")
    
    con = get_database_connection()
    
    try:
        # Build filter query based on session state
        filter_query = build_filter_query()
        
        # Total Order Value
        total_order_value_query = f"""
            SELECT SUM(ord.total_amount) as total_order_value
            FROM orders ord
            JOIN outlets o ON ord.outlet_id = o.outlet_id
            {filter_query}
        """
        total_order_value = con.execute(total_order_value_query).fetchone()[0] or 0
        st.metric("Total Order Value", f"₹{total_order_value:,.2f}")
        
        # Average Order Value
        avg_order_value_query = f"""
            SELECT AVG(ord.total_amount) as avg_order_value
            FROM orders ord
            JOIN outlets o ON ord.outlet_id = o.outlet_id
            {filter_query}
        """
        avg_order_value = con.execute(avg_order_value_query).fetchone()[0] or 0
        st.metric("Average Order Value", f"₹{avg_order_value:,.2f}")
        
        # PCs that contribute to top 10% of order value
        st.write("Outlets Contributing to Top 10% of Order Value")
        top_10_percent_query = f"""
            WITH OutletTotals AS (
                SELECT 
                    o.outlet_id,
                    o.outlet_name,
                    o.region,
                    SUM(ord.total_amount) as total_order_value,
                    SUM(SUM(ord.total_amount)) OVER () as grand_total
                FROM orders ord
                JOIN outlets o ON ord.outlet_id = o.outlet_id
                {filter_query}
                GROUP BY o.outlet_id, o.outlet_name, o.region
            ),
            CumulativeTotals AS (
                SELECT 
                    outlet_id,
                    outlet_name,
                    region,
                    total_order_value,
                    grand_total,
                    SUM(total_order_value) OVER (ORDER BY total_order_value DESC) as cumulative_value,
                    SUM(total_order_value) OVER (ORDER BY total_order_value DESC) / grand_total as cumulative_percentage
                FROM OutletTotals
            )
            SELECT 
                outlet_id,
                outlet_name,
                region,
                total_order_value,
                cumulative_percentage * 100 as cumulative_percentage
            FROM CumulativeTotals
            WHERE cumulative_percentage <= 0.1
            ORDER BY total_order_value DESC
        """
        top_10_percent_data = con.execute(top_10_percent_query).fetchdf()
        
        if not top_10_percent_data.empty:
            st.dataframe(top_10_percent_data)
            fig = px.bar(top_10_percent_data, x="outlet_name", y="total_order_value", color="region", 
                         title="Outlets Contributing to Top 10% of Order Value")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected filters.")
            
    except Exception as e:
        st.error(f"Error in Order Performance - Order Value: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()