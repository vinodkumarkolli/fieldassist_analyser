import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DATABASE_PATH

def get_database_connection():
    return duckdb.connect(DATABASE_PATH)

def app():
    st.subheader("Comparative Analysis")
    
    con = get_database_connection()
    
    try:
        # File upload for present day sales data
        st.write("Upload Present Day Sales Data")
        uploaded_file = st.file_uploader("Choose an Excel file with present day sales data", type=["xlsx"])
        
        if uploaded_file is not None:
            # Read the uploaded file
            present_day_data = pd.read_excel(uploaded_file)
            st.write(f"Uploaded file contains {len(present_day_data)} records")
            
            # Display first few rows of uploaded data
            st.write("Preview of uploaded data:")
            st.dataframe(present_day_data.head())
            
            # Extract outlet details from uploaded data
            if 'Outlet Erp Id' in present_day_data.columns:
                uploaded_outlets = present_day_data['Outlet Erp Id'].unique()
                st.write(f"Number of unique outlets in uploaded data: {len(uploaded_outlets)}")
                
                # Date range selector for historic sales period
                st.write("Select Historic Sales Period")
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=pd.to_datetime("2025-01-01"))
                with col2:
                    end_date = st.date_input("End Date", value=pd.to_datetime("2025-08-31"))
                
                # Convert date range to month format (MM-YY) for filtering
                # We'll filter data from the database based on the selected date range
                start_month = start_date.strftime("%m-%y")
                end_month = end_date.strftime("%m-%y")
                
                if st.button("Perform Comparative Analysis"):
                    # Fetch historic data for the selected outlets and period
                    with st.spinner("Fetching historic data..."):
                        # Get historic data for the outlets in the uploaded file
                        outlet_ids_str = "', '".join(uploaded_outlets.astype(str))
                        outlet_ids_str = f"'{outlet_ids_str}'"
                        
                        # Get all available months in the database to filter based on date range
                        all_months = con.execute("SELECT DISTINCT order_month FROM orders ORDER BY order_month").fetchall()
                        all_months = [row[0] for row in all_months]
                        
                        # Filter months based on the selected date range
                        # This is a simplified approach - in a real implementation, you might need more sophisticated date filtering
                        filtered_months = []
                        for month in all_months:
                            try:
                                month_date = pd.to_datetime(month, format="%m-%y")
                                # Convert datetime.date to pd.Timestamp for comparison
                                start_timestamp = pd.Timestamp(start_date)
                                end_timestamp = pd.Timestamp(end_date)
                                if start_timestamp <= month_date <= end_timestamp:
                                    filtered_months.append(month)
                            except Exception:
                                # Skip months that can't be parsed
                                continue
                        
                        if filtered_months:
                            months_str = "', '".join(filtered_months)
                            months_str = f"'{months_str}'"
                            
                            historic_query = f"""
                                SELECT
                                    o.outlet_id,
                                    o.outlet_name,
                                    ord.order_month,
                                    SUM(ord.total_amount) as monthly_sales
                                FROM orders ord
                                JOIN outlets o ON ord.outlet_id = o.outlet_id
                                WHERE ord.outlet_id IN ({outlet_ids_str})
                                AND ord.order_month IN ({months_str})
                                GROUP BY o.outlet_id, o.outlet_name, ord.order_month
                                ORDER BY o.outlet_id, ord.order_month
                            """
                            
                            historic_data = con.execute(historic_query).fetchdf()
                            
                            if not historic_data.empty:
                                # Calculate month-wise historic orders value
                                monthly_historic = historic_data.groupby('order_month')['monthly_sales'].sum().reset_index()
                                monthly_historic = monthly_historic.sort_values('order_month')
                                
                                st.write("Historic Data Comparison:")
                                # Pivot the data to show months as columns
                                pivot_data = historic_data.pivot_table(
                                    index=['outlet_id', 'outlet_name'],
                                    columns='order_month',
                                    values='monthly_sales',
                                    aggfunc='sum',
                                    fill_value=0
                                ).reset_index()
                                
                                # Add L1Position and User from uploaded file to the pivot table
                                if 'L1Position' in present_day_data.columns or 'User' in present_day_data.columns:
                                    # Get L1Position and User for each outlet from the uploaded file
                                    merge_columns = ['Outlet Erp Id']
                                    if 'L1Position' in present_day_data.columns:
                                        merge_columns.append('L1Position')
                                    if 'User' in present_day_data.columns:
                                        merge_columns.append('User')
                                    
                                    info_by_outlet = present_day_data[merge_columns].drop_duplicates()
                                    info_by_outlet.columns = ['outlet_id'] + [col for col in merge_columns if col != 'Outlet Erp Id']
                                    
                                    # Merge with pivot data
                                    pivot_data = pivot_data.merge(info_by_outlet, on='outlet_id', how='left')
                                
                                # Add present day sales data to the pivot table
                                if 'Net Value Tax Inclusive' in present_day_data.columns:
                                    # Group present day data by outlet
                                    present_day_by_outlet = present_day_data.groupby('Outlet Erp Id')['Net Value Tax Inclusive'].sum().reset_index()
                                    present_day_by_outlet.columns = ['outlet_id', 'present_day_sales']
                                    
                                    # Merge with pivot data
                                    pivot_data = pivot_data.merge(present_day_by_outlet, on='outlet_id', how='left')
                                    
                                    # Calculate last month sales for each outlet
                                    # Get the last month in the historic data
                                    if len(monthly_historic) > 1:
                                        # Get the most recent month from the historic data
                                        last_month = monthly_historic.iloc[-1]['order_month']  # Last month in the data
                                        
                                        # Calculate percentage change from last month
                                        # This compares present day sales with the last month's historic sales
                                        if last_month in pivot_data.columns:
                                            # Get last month sales for each outlet from the historic data
                                            last_month_outlet_data = historic_data[historic_data['order_month'] == last_month]
                                            last_month_by_outlet = last_month_outlet_data.groupby('outlet_id')['monthly_sales'].sum().reset_index()
                                            last_month_by_outlet.columns = ['outlet_id', 'last_month_sales']
                                            
                                            # Merge last month sales with pivot data
                                            pivot_data = pivot_data.merge(last_month_by_outlet, on='outlet_id', how='left')
                                            pivot_data['last_month_sales'] = pivot_data['last_month_sales'].fillna(0)
                                            
                                            # Calculate percentage change: ((present - last_month) / last_month) * 100
                                            # Replace 0 values with NaN to avoid division by zero
                                            last_month_sales_for_calc = pivot_data['last_month_sales'].replace(0, pd.NA)
                                            pct_change = ((pivot_data['present_day_sales'] - last_month_sales_for_calc) / last_month_sales_for_calc * 100)
                                            # Fill NaN values with 0 (when last_month_sales was 0) and round to 2 decimal places
                                            pivot_data['pct_change_from_last_month'] = pct_change.fillna(0).infer_objects(copy=False).round(2)
                                        else:
                                            pivot_data['pct_change_from_last_month'] = 0
                                        
                                        # Calculate percentage change from average
                                        # This compares present day sales with the average historic sales
                                        avg_sales = monthly_historic['monthly_sales'].mean()
                                        # Replace 0 values with NaN to avoid division by zero
                                        avg_sales_for_calc = avg_sales if avg_sales != 0 else pd.NA
                                        if pd.notna(avg_sales_for_calc):
                                            pct_change_avg = ((pivot_data['present_day_sales'] - avg_sales_for_calc) / avg_sales_for_calc * 100)
                                            # Fill NaN values with 0 (when avg_sales was 0) and round to 2 decimal places
                                            pivot_data['pct_change_from_avg'] = pct_change_avg.fillna(0).infer_objects(copy=False).round(2)
                                        else:
                                            pivot_data['pct_change_from_avg'] = 0
                                
                                st.dataframe(pivot_data)
                                
                                # Calculate average sales
                                avg_sales = monthly_historic['monthly_sales'].mean()
                                
                                # Calculate percentage differences
                                monthly_historic['pct_from_avg'] = ((monthly_historic['monthly_sales'] - avg_sales) / avg_sales) * 100
                                
                                # Calculate percentage difference from previous month
                                monthly_historic['pct_from_prev_month'] = monthly_historic['monthly_sales'].pct_change() * 100
                                
                                st.write("Monthly Historic Sales Analysis:")
                                st.dataframe(monthly_historic)
                                
                                # Display average sales
                                st.write(f"Average Monthly Sales: ₹{avg_sales:,.2f}")
                                
                                # Create visualization
                                fig = px.line(monthly_historic, x='order_month', y='monthly_sales',
                                              title='Monthly Historic Sales Trend')
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Bar chart for percentage differences
                                fig2 = go.Figure(data=[
                                    go.Bar(name='From Average', x=monthly_historic['order_month'],
                                          y=monthly_historic['pct_from_avg']),
                                    go.Bar(name='From Previous Month', x=monthly_historic['order_month'],
                                          y=monthly_historic['pct_from_prev_month'])
                                ])
                                fig2.update_layout(title='Percentage Differences',
                                                  yaxis_title='Percentage Change (%)')
                                st.plotly_chart(fig2, use_container_width=True)
                            else:
                                st.warning("No historic data found for the selected outlets and date range.")
                        else:
                            st.warning("No months found within the selected date range.")
            else:
                st.error("Uploaded file does not contain 'Outlet Erp Id' column. Please check the file format.")
        else:
            st.info("Please upload a file to begin comparative analysis.")
    except Exception as e:
        st.error(f"Error in Comparative Analysis: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    app()