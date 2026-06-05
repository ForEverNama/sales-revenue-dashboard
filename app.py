import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Sales & Revenue Dashboard", layout="wide")
st.title("📊 Sales & Revenue Analysis Dashboard")
st.markdown("Upload your sales data (CSV or Excel) to analyze key performance metrics.")

# File Uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data based on file type
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Ensure date column is datetime format if it exists
        date_col = [col for col in df.columns if 'date' in col.lower()]
        if date_col:
            df[date_col[0]] = pd.to_datetime(df[date_col[0]])
            df = df.sort_values(by=date_col[0])

        st.success("Data loaded successfully!")
        
        # --- SIDEBAR FILTERS ---
        st.sidebar.header("Filter Options")
        
        # Dynamic filters based on column existence
        category_col = [col for col in df.columns if 'category' in col.lower() or 'type' in col.lower()]
        region_col = [col for col in df.columns if 'region' in col.lower() or 'location' in col.lower()]
        
        selected_category = "All"
        if category_col:
            categories = ["All"] + list(df[category_col[0]].unique())
            selected_category = st.sidebar.selectbox("Select Category", categories)
            
        selected_region = "All"
        if region_col:
            regions = ["All"] + list(df[region_col[0]].unique())
            selected_region = st.sidebar.selectbox("Select Region", regions)

        # Apply Filters
        filtered_df = df.copy()
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df[category_col[0]] == selected_category]
        if selected_region != "All":
            filtered_df = filtered_df[filtered_df[region_col[0]] == selected_region]

        # --- KPI METRICS ---
        # Look for standard column names
        revenue_col = [col for col in df.columns if 'revenue' in col.lower() or 'sales' in col.lower() or 'amount' in col.lower()][0]
        quantity_col = [col for col in df.columns if 'quantity' in col.lower() or 'qty' in col.lower() or 'units' in col.lower()]
        product_col = [col for col in df.columns if 'product' in col.lower() or 'item' in col.lower()][0]

        total_revenue = filtered_df[revenue_col].sum()
        total_orders = len(filtered_df)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${total_revenue:,.2f}")
        col2.metric("Total Orders", f"{total_orders:,}")
        col3.metric("Average Order Value", f"${avg_order_value:,.2f}")

        st.markdown("---")

        # --- VISUALIZATIONS ---
        left_chart_col, right_chart_col = st.columns(2)

        # 1. Revenue Trend Line Chart
        with left_chart_col:
            st.subheader("📈 Revenue Trend Over Time")
            if date_col:
                trend_df = filtered_df.groupby(date_col[0])[revenue_col].sum().reset_index()
                fig_trend = px.line(trend_df, x=date_col[0], y=revenue_col, labels={revenue_col: "Revenue"})
                st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("Add a 'Date' column to view revenue trends over time.")

        # 2. Top Performing Products Bar Chart
        with right_chart_col:
            st.subheader("🏆 Top Performing Products")
            top_products = filtered_df.groupby(product_col)[revenue_col].sum().reset_index()
            top_products = top_products.sort_values(by=revenue_col, ascending=False).head(10)
            fig_products = px.bar(top_products, x=revenue_col, y=product_col, orientation='h', 
                                 labels={revenue_col: "Total Revenue", product_col: "Product"})
            fig_products.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_products, use_container_width=True)

        # --- DATA TABLE VIEW ---
        st.markdown("---")
        st.subheader("📋 Filtered Data Preview")
        st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error parsing file: {e}. Please ensure your dataset contains standard sales columns (Date, Revenue/Sales, Product).")

else:
    st.info("Waiting for data upload. Please upload an Excel or CSV file to begin.")
