# streamlit_ola_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import duckdb

# -------------------------
# CONFIG
# -------------------------
DATA_PATH = r"E:\project labmentix\ola ride project\ola_cleaned.csv"
st.set_page_config(layout="wide", page_title="Ola Rides Dashboard")

# -------------------------
# LOAD & PREP DATA
# -------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    if "datetime" in df.columns and "Date" not in df.columns:
        df["Date"] = pd.to_datetime(df["datetime"], errors="coerce")

    if "Payment_Method" in df.columns:
        df["Payment_Method_norm"] = df["Payment_Method"].astype(str).str.strip().str.upper()
    else:
        df["Payment_Method_norm"] = np.nan

    if "Booking_Status" in df.columns:
        df["Booking_Status_norm"] = df["Booking_Status"].astype(str).str.strip()
    else:
        df["Booking_Status_norm"] = np.nan

    return df

df = load_data(DATA_PATH)

if df.empty:
    st.error(f"CSV not found or empty at: {DATA_PATH}")
    st.stop()

# -------------------------
# CUSTOM TITLE WITH OLA COLORS
# -------------------------
st.markdown(
    """
    <h1 style="
        text-align: center; 
        color: #000000; 
        background: linear-gradient(90deg, #FDD835, #4A4A4A); 
        padding: 20px; 
        border-radius: 15px; 
        box-shadow: 0px 8px 15px rgba(0,0,0,0.4); 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 35px;
    ">
        🚖 Ola Rides — <span style="color:#ffffff;">Interactive Analytics Dashboard</span>
    </h1>
    """,
    unsafe_allow_html=True
)

# Add space 
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("Use the sidebar filters. Explore data via tabs or run custom SQL queries.")

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.header("🔎 Filters & Search")

# Vehicle Type
vehicle_options = list(df["Vehicle_Type"].dropna().unique()) if "Vehicle_Type" in df.columns else []
sel_vehicle = st.sidebar.multiselect("Vehicle Type", options=vehicle_options, default=vehicle_options)

# Booking Status
status_options = list(df["Booking_Status_norm"].dropna().unique()) if "Booking_Status_norm" in df.columns else []
sel_status = st.sidebar.multiselect("Booking Status", options=status_options, default=status_options)

# Payment Method
payment_options = sorted(df["Payment_Method_norm"].dropna().unique()) if "Payment_Method_norm" in df.columns else []
sel_payment = st.sidebar.multiselect("Payment Method", options=payment_options, default=payment_options)

# Date Range
if "Date" in df.columns:
    dt_min, dt_max = df["Date"].min().date(), df["Date"].max().date()
    sel_date = st.sidebar.date_input("Date range", value=(dt_min, dt_max), min_value=dt_min, max_value=dt_max)
else:
    sel_date = None

# Search
st.sidebar.markdown("---")
cust_search = st.sidebar.text_input("🔍 Search Customer ID", "")
booking_search = st.sidebar.text_input("🔍 Search Booking ID", "")

# -------------------------
# APPLY FILTERS
# -------------------------
df_filtered = df.copy()

if sel_vehicle and "Vehicle_Type" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Vehicle_Type"].isin(sel_vehicle)]

if sel_status and "Booking_Status_norm" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Booking_Status_norm"].isin(sel_status)]

if sel_payment:
    df_filtered = df_filtered[df_filtered["Payment_Method_norm"].isin(sel_payment)]

if sel_date and "Date" in df_filtered.columns:
    d0, d1 = pd.to_datetime(sel_date[0]), pd.to_datetime(sel_date[1])
    df_filtered = df_filtered[(df_filtered["Date"] >= d0) & (df_filtered["Date"] <= d1)]

if cust_search and "Customer_ID" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Customer_ID"].astype(str).str.contains(cust_search, case=False, na=False)]

if booking_search and "Booking_ID" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Booking_ID"].astype(str).str.contains(booking_search, case=False, na=False)]

st.sidebar.markdown(f"**Filtered rows:** {len(df_filtered):,}")

# -------------------------
# KPIs Section (Filtered Data)
# -------------------------
st.markdown("### 📌 Key Metrics")

# Custom CSS for small metric cards
st.markdown(
    """
    <style>
    .small-metric {
        padding: 10px 15px;
        border-radius: 10px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.2);
        text-align: center;
        color: #000000;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .small-metric-label {
        font-size: 15px;
        font-weight: 500;
        color: #222;
    }
    .small-metric-value {
        font-size: 18px;
        font-weight: 700;
        color: #000;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div class="small-metric">
            <div class="small-metric-label">Total Rides</div>
            <div class="small-metric-value">{len(df_filtered):,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if "Booking_Status_norm" in df_filtered.columns:
        total = len(df_filtered)
        cancelled = df_filtered["Booking_Status_norm"].str.contains("Cancel", case=False, na=False).sum()
        cancel_pct = f"{(cancelled/total*100):.2f}%" if total > 0 else "N/A"
        st.markdown(
            f"""
            <div class="small-metric">
                <div class="small-metric-label">Cancellation %</div>
                <div class="small-metric-value">{cancel_pct}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

with col3:
    if {"Booking_Value", "Booking_Status_norm"}.issubset(df_filtered.columns):
        total_revenue = df_filtered[df_filtered["Booking_Status_norm"] == "Success"]["Booking_Value"].sum()
        st.markdown(
            f"""
            <div class="small-metric">
                <div class="small-metric-label">Revenue (Success)</div>
                <div class="small-metric-value">₹{total_revenue:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Add space 
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# MAIN NAVIGATION TABS
# -------------------------
tab_sql, tab_powerbi = st.tabs(["📝 SQL Queries", "📈 Power BI Interactive Dashboard"])

# -------------------------
# SQL TAB
# -------------------------
with tab_sql:
    st.header("📝 Run SQL Queries on Filtered Data")
   
    # -------------------------
    # PREDEFINED SQL QUERIES
    # -------------------------
    sql_queries = {
        "1. Retrieve all successful bookings": """
            SELECT *
            FROM df_filtered
            WHERE Booking_Status = 'Success'
        """,

        "2. Find the average ride distance for each vehicle type": """
            SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance
            FROM df_filtered
            GROUP BY Vehicle_Type
        """,

        "3. Get the total number of cancelled rides by customers": """
            SELECT COUNT(*) AS cancelled_by_customers
            FROM df_filtered
            WHERE Booking_Status = 'Cancelled by Customer'
        """,

        "4. List the top 5 customers who booked the highest number of rides": """
            SELECT Customer_ID, COUNT(*) AS total_rides
            FROM df_filtered
            GROUP BY Customer_ID
            ORDER BY total_rides DESC
            LIMIT 5
        """,

        "5. Get the number of rides cancelled by drivers due to personal and car-related issues": """
            SELECT COUNT(*)
            FROM df_filtered
            WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';
        """,

        "6. Find the maximum and minimum driver ratings for Prime Sedan bookings": """
            SELECT MAX(Driver_Ratings) AS max_rating,
                   MIN(Driver_Ratings) AS min_rating
            FROM df_filtered
            WHERE Vehicle_Type = 'Prime Sedan'
        """,

        "7. Retrieve all rides where payment was made using UPI": """
            SELECT *
            FROM df_filtered
            WHERE Payment_Method = 'Upi'
        """,

        "8. Find the average customer rating per vehicle type": """
            SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_rating
            FROM df_filtered
            GROUP BY Vehicle_Type
        """,

        "9. Calculate the total booking value of rides completed successfully": """
            SELECT SUM(Booking_Value) AS total_success_value
            FROM df_filtered
            WHERE Booking_Status = 'Success'
        """,

        "10. List all incomplete rides along with the reason": """
            SELECT *
            FROM df_filtered
            WHERE Incomplete_Rides = 'Yes';
        """
    }

    # -------------------------
    # Query UI
    # -------------------------
    selected_query = st.selectbox("Choose a predefined query", list(sql_queries.keys()))
    sql_to_run = sql_queries[selected_query]

    # Editable text area
    user_query = st.text_area("SQL Editor", sql_to_run, height=150)

    # Run query button
    if st.button("▶ Run Query"):
        try:
            result = duckdb.query(user_query).to_df()
            st.dataframe(result, use_container_width=True)

            # Optional chart (for simple aggregations)
            if result.shape[1] == 2 and pd.api.types.is_numeric_dtype(result.iloc[:, 1]):
                fig = px.bar(result, x=result.columns[0], y=result.columns[1], title=selected_query)
                st.plotly_chart(fig, use_container_width=True, key="sql_chart")

            # CSV download
            csv = result.to_csv(index=False).encode("utf-8")
            st.download_button("💾 Download Results as CSV", csv, "query_results.csv", "text/csv")

        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

# -------------------------
# Power Bi Interactive Dashboard Sub Tabs
# -------------------------
with tab_powerbi:
    st.header("📈 Power BI Interactive Dashboard")

    sub_overall, sub_vehicle, sub_revenue, sub_cancel, sub_ratings = st.tabs(
        ["📈 Overall", "🚘 Vehicle Type", "💰 Revenue", "❌ Cancellation", "⭐ Ratings"]
    )

# -------------------------
# OVERALL Tab
# -------------------------
with sub_overall:
    st.subheader("📈 Ride Volume Over Time")
    if "Date" in df_filtered.columns:
        daily = df_filtered.groupby(df_filtered["Date"].dt.date).size().reset_index(name="ride_count")
        fig = px.line(daily, x="Date", y="ride_count", markers=True, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Booking Status Breakdown")
    if "Booking_Status_norm" in df_filtered.columns:
        status_counts = df_filtered["Booking_Status_norm"].value_counts().reset_index()
        status_counts.columns = ["Booking_Status", "count"]
        fig = px.pie(status_counts, names="Booking_Status", values="count", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# VEHICLE Tab
# -------------------------
    with sub_vehicle:
        st.subheader("🚘 Top Vehicle Types by Distance")
        if {"Vehicle_Type", "Ride_Distance"}.issubset(df_filtered.columns):
            agg = df_filtered.groupby("Vehicle_Type")["Ride_Distance"].sum().reset_index()
            agg = agg.sort_values("Ride_Distance", ascending=False).head(5)
            fig = px.bar(agg, x="Vehicle_Type", y="Ride_Distance", template="plotly_white", color="Ride_Distance")
            st.plotly_chart(fig, use_container_width=True, key="vehicle_type")

# -------------------------
# REVENUE Tab
# -------------------------
with sub_revenue:
    st.subheader("💰 Revenue by Payment Method")

    if {"Payment_Method", "Booking_Value"}.issubset(df_filtered.columns):
        rev = (
            df_filtered[df_filtered["Payment_Method"].str.lower() != "unknown"]  # 🚫 remove Unknown
            .groupby("Payment_Method")["Booking_Value"]
            .sum()
            .reset_index()
            .sort_values("Booking_Value", ascending=False)
        )

        fig = px.bar(
            rev,
            x="Payment_Method",
            y="Booking_Value",
            text="Booking_Value",
            title="Revenue by Payment Method",
            template="plotly_white",
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition="outside")
        fig.update_layout(yaxis_title="Revenue", xaxis_title="Payment Method")
        st.plotly_chart(fig, use_container_width=True, key="revenue_method_bar")
     
    st.subheader("🏆 Top 5 Customers by Total Booking Value")
    if {"Customer_ID", "Booking_Value"}.issubset(df_filtered.columns):
        topcust = df_filtered.groupby("Customer_ID")["Booking_Value"].sum().reset_index()
        topcust = topcust.sort_values("Booking_Value", ascending=False).head(5)
        fig = px.bar(topcust, x="Customer_ID", y="Booking_Value", template="plotly_white", color="Booking_Value")
        st.plotly_chart(fig, use_container_width=True, key="top_customers")

    st.subheader("📊 Ride Distance Distribution Per Day")
    if {"Date", "Ride_Distance"}.issubset(df_filtered.columns):
         df_filtered["date_only"] = df_filtered["Date"].dt.date
         dist_per_day = (df_filtered.groupby("date_only")["Ride_Distance"].mean().reset_index().sort_values("date_only"))

    fig = px.bar(
        dist_per_day,
        x="date_only",
        y="Ride_Distance",
        text="Ride_Distance",
        title="Average Ride Distance Per Day",
        template="plotly_white",
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition="outside")
    fig.update_layout(yaxis_title="Avg Ride Distance", xaxis_title="Date")

    st.plotly_chart(fig, use_container_width=True, key="distance_distribution_bar")

# -------------------------
# CANCELLATION Tab
# -------------------------
with sub_cancel:
    st.subheader("❌ Cancellation Reasons")

    # 1️⃣ Customer cancellations
    if "Canceled_Rides_by_Customer" in df_filtered.columns:
        reasons_customer = (
            df_filtered.loc[df_filtered["Canceled_Rides_by_Customer"].notna() &
                            (df_filtered["Canceled_Rides_by_Customer"].str.lower() != "not applicable"),
                            "Canceled_Rides_by_Customer"]
            .value_counts()
            .reset_index()
        )
        reasons_customer.columns = ["Reason", "Count"]

        if not reasons_customer.empty:
            fig1 = px.pie(
                reasons_customer.head(10),
                names="Reason",
                values="Count",
                template="plotly_white",
                title="Cancelled Rides Reasons (Customer)"
            )
            st.plotly_chart(fig1, use_container_width=True, key="cancel_customer")

    # 2️⃣ Driver cancellations
    if "Canceled_Rides_by_Driver" in df_filtered.columns:
        reasons_driver = (
            df_filtered.loc[df_filtered["Canceled_Rides_by_Driver"].notna() &
                            (df_filtered["Canceled_Rides_by_Driver"].str.lower() != "not applicable"),
                            "Canceled_Rides_by_Driver"]
            .value_counts()
            .reset_index()
        )
        reasons_driver.columns = ["Reason", "Count"]

        if not reasons_driver.empty:
            fig2 = px.pie(
                reasons_driver.head(10),
                names="Reason",
                values="Count",
                template="plotly_white",
                title="Cancelled Rides Reasons (Driver)"
            )
            st.plotly_chart(fig2, use_container_width=True, key="cancel_driver")

# -------------------------
# RATINGS Tab
# -------------------------
with sub_ratings:
    st.subheader("⭐ Ratings Overview")

    col1, col2 = st.columns(2)

    # 1️⃣ Driver Ratings Distribution
    with col1:
        if "Driver_Ratings" in df_filtered.columns:
            driver_ratings = (
                df_filtered["Driver_Ratings"]
                .dropna()
                .value_counts()
                .reset_index()
            )
            driver_ratings.columns = ["Rating", "Count"]  # rename properly
            driver_ratings = driver_ratings.sort_values("Rating")  # now Rating exists

            fig_driver = px.bar(
                driver_ratings,
                x="Rating",
                y="Count",
                title="Driver Ratings Distribution",
                template="plotly_white",
            )
            st.plotly_chart(fig_driver, use_container_width=True, key="driver_ratings_bar")

    # 2️⃣ Customer Ratings Distribution
    with col2:
        if "Customer_Rating" in df_filtered.columns:
            customer_ratings = (
                df_filtered["Customer_Rating"]
                .dropna()
                .value_counts()
                .reset_index()
            )
            customer_ratings.columns = ["Rating", "Count"]  # rename properly
            customer_ratings = customer_ratings.sort_values("Rating")  # safe

            fig_customer = px.bar(
                customer_ratings,
                x="Rating",
                y="Count",
                title="Customer Ratings Distribution",
                template="plotly_white",
            )
            st.plotly_chart(fig_customer, use_container_width=True, key="customer_ratings_bar")

def chart_card(title, fig, key=None):
    """
    Wraps a chart inside a styled white card
    """
    st.markdown(
        f"""
        <div class="chart-card">
            <h4>{title}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.plotly_chart(fig, use_container_width=True, key=key)
    

