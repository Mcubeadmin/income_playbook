import io
import msoffcrypto
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Account Statement Dashboard",
    page_icon="🏦",
    layout="wide"  # <--- This instantly expands your narrow central column!
)

# Set up the title of the web page
st.title("🏦 Account Statement Dashboard")
st.markdown("Upload your encrypted Excel statement to visualize your financial trends.")


# Create a reusable function out of your existing parsing code
def process_statement(uploaded_file, password):
    try:
        decrypted = io.BytesIO()
        # Read the uploaded file bytes directly from Streamlit's memory buffer
        file = msoffcrypto.OfficeFile(uploaded_file)
        file.load_key(password=password)
        file.decrypt(decrypted)

        # Your exact Pandas logic
        df = pd.read_excel(decrypted, skiprows=17, skipfooter=8)

        # Clean up data types for flawless plotting
        df.columns = df.columns.str.strip()
        df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")

        return df
    except Exception as e:
        st.error(f"Decryption failed. Please check your password. Error: {e}")
        return None


# --- STREAMLIT SIDEBAR / INTERFACE CONTROLS ---
st.sidebar.header("Settings")

# 1. File Uploader widget
uploaded_file = st.sidebar.file_uploader(
    "Select your account statement", type=["xls", "xlsx"]
)

# 2. Secure Password Input widget
password = st.sidebar.text_input("Enter Statement Password", type="password")

# 3. Dynamic Chart Layout Toggle (NEW)
st.sidebar.markdown("---")
st.sidebar.subheader("Visualization Options")
chart_view = st.sidebar.radio(
    "Select Chart View Layout:",
    options=["Combined Trend (All-in-One)", "Separate Detailed Charts (deprecated)"],
)

# --- MAIN PAGE LOGIC ---
if uploaded_file and password:

    # Run your processing logic
    df = process_statement(uploaded_file, password)

    if df is not None and not df.empty:
        # popup success message after loading data
        st.toast("Data successfully loaded!")

        # --- 1. Clean up the Balance, Debit, and Credit columns ---
        for col in ["Balance", "Debit", "Credit"]:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.replace(",", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Fill missing values (NaN) with 0 for tracking lines smoothly
        df["Debit"] = df["Debit"].fillna(0)
        df["Credit"] = df["Credit"].fillna(0)

        # Drop any remaining unparsed dates, and sort chronologically
        df = df.dropna(subset=["Date"]).sort_values(by="Date")

        # Metric Displays for quick insights
        latest_balance = df["Balance"].iloc[-1]
        st.metric(label="Current Balance", value=f"₹{latest_balance:,.2f}")

        # Date range variables for chart titles
        start_date = df["Date"].dt.strftime("%d %b %Y").iloc[0]
        end_date = df["Date"].dt.strftime("%d %b %Y").iloc[-1]

        # --- 2. Render Selection Logic ---
        if chart_view == "Combined Trend (All-in-One)":
            st.subheader("📊 Financial Activity Over Time (Combined)")
            st.caption("💡 **Pro-Tip:** Click on any point on the chart line to anchor and display full transaction logs down below.")

            # 1. Build the clean baseline chart (Turn off the floating hover tooltip completely)
            fig_combined = px.line(
                df,
                x="Date",
                y="Balance",
                title=f"Statement Trends: {start_date} - {end_date}",
                labels={"Date": "Transaction Date", "Balance": "Account Balance (₹)"},
            )
            
            fig_combined.update_traces(
                mode="lines+markers",
                marker=dict(size=6, color="#55e32a"),
                line=dict(width=2, color="#1f77b4"),
                # This completely disables the floating pop-up card over the chart!
                hoverinfo="skip" 
            )
            
            fig_combined.update_layout(
                xaxis_tickangle=45,
                clickmode="event+select" # Configures Plotly to register click states
            )
            
            # Add intersecting crosshair guidelines so you see exactly what you are pointing at
            fig_combined.update_xaxes(showspikes=True, spikecolor="gray", spikethickness=1, spikemode="across")
            fig_combined.update_yaxes(showspikes=True, spikecolor="gray", spikethickness=1)

            # 2. Render the chart and tell Streamlit to listen to click events
            # 'on_select="rerun"' forces Streamlit to update the page components immediately when a dot is clicked
            event_data = st.plotly_chart(fig_combined, width='stretch', on_select="rerun")

            # 3. INTERACTIVE BOX: Catch click actions and print the target data row
            # If a point is selected, display a prominent metadata container box right below the graph
            if event_data and "selection" in event_data and "points" in event_data["selection"] and len(event_data["selection"]["points"]) > 0:
                selected_point = event_data["selection"]["points"][0]
                point_index = selected_point["point_index"]
                
                # Pull the precise row corresponding to the clicked coordinate index
                row = df.iloc[point_index]
                
                # Format an elegant layout container box for the clicked transaction
                st.markdown("---")
                st.markdown("### 🔍 Inspected Transaction Details")
                
                # Create a 4-column metric strip for crisp layout reading
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("📅 Date", row["Date"].strftime("%d %b %Y"))
                
                if row["Debit"] > 0:
                    m2.metric("🛑 Outgoing Debit", f"₹{row['Debit']:,.2f}", delta="- Expenses", delta_color="inverse")
                else:
                    m2.metric("🛑 Outgoing Debit", "₹0.00")
                    
                if row["Credit"] > 0:
                    m3.metric("🟢 Incoming Credit", f"₹{row['Credit']:,.2f}", delta="+ Earnings")
                else:
                    m3.metric("🟢 Incoming Credit", "₹0.00")
                m4.metric("💰 Running Balance", f"₹{row['Balance']:,.2f}")
                
                # Output the long narration details full-width across the bottom
                st.markdown(f"**Bank Transaction String Description:**\n\n`{row['Details']}`")
            else:
                # Fallback message shown when nothing has been clicked yet
                st.info("👆 Click on any milestone coordinate dot on the chart timeline above to populate the specific transaction details here.")
        else:
            st.subheader("📋 Split Metric Analysis")

            # Chart 1: Balance over time (Blue line)
            fig_bal = px.line(
                df,
                x="Date",
                y="Balance",
                hover_data=["Details", "Debit", "Credit"],
                title=f"Account Balance Progression ({start_date} - {end_date})",
                labels={"Date": "Transaction Date", "Balance": "Balance (₹)"},
            )
            fig_bal.update_traces(line_color="#1f77b4", mode="lines+markers", marker=dict(size=4))
            st.plotly_chart(fig_bal, width='stretch')

            # Use st.columns to put Debit and Credit charts side-by-side!
            col_left, col_right = st.columns(2)

            with col_left:
                # Chart 2: Debits (Red line/markers)
                fig_deb = px.bar(  # Switching to a Bar chart makes single expenses pop nicely!
                    df[df["Debit"] > 0],
                    x="Date",
                    y="Debit",
                    hover_data=["Details"],
                    title="Outgoing Debits (Expenses)",
                    labels={"Date": "Transaction Date", "Debit": "Debit Amount (₹)"},
                )
                fig_deb.update_traces(marker_color="#d62728")
                st.plotly_chart(fig_deb, width='stretch')

            with col_right:
                # Chart 3: Credits (Green line/markers)
                fig_cred = px.bar(
                    df[df["Credit"] > 0],
                    x="Date",
                    y="Credit",
                    hover_data=["Details"],
                    title="Incoming Credits (Earnings)",
                    labels={"Date": "Transaction Date", "Credit": "Credit Amount (₹)"},
                )
                fig_cred.update_traces(marker_color="#2ca02c")
                st.plotly_chart(fig_cred, width='stretch')

        # 4. Show raw Data Table underneath
        with st.expander("🔍 View Raw Transaction Data Table"):
            st.dataframe(df)

    # --- Place this section right under your plotting logic ---

    st.markdown("---")
    st.subheader("🔍 Advanced Transaction Search & Filtering")

    # 1. Date Range Slider Control
    # Get the minimum and maximum dates present in your actual statement
    if not df["Date"].isnull().all():
        min_date = df["Date"].min().to_pydatetime()
        max_date = df["Date"].max().to_pydatetime()

        # Create a range slider where the user sweeps across timestamps
        selected_date_range = st.slider(
            "Select Date Range Range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),  # Default positions: spans full statement
            format="DD MMM YYYY",
        )

        # Filter the primary dataframe based on the slider bounds
        start_date, end_date = selected_date_range
        selected_data = df[df["Date"].between(start_date, end_date)]
    else:
        selected_data = df.copy()

    # 2. Text Box Input for Keywords
    search_query = st.text_input(
        "Enter filter words / phrases (separate multiple words with commas):",
        placeholder="e.g., MUJIP, ZERODHA, SWIGGY",
    ).strip()


    # 1. Add a layout toggle switch under your text input bar
    search_mode = st.radio(
        "Search Mode:",
        options=["Match ANY word (OR)", "Match ALL words (AND)"],
        horizontal=True
    )

    # 2. Update your processing function to handle the selection
    def filter_search(df_to_filter, phrases_str, mode):
        if not phrases_str:
            return df_to_filter

        phrases = [p.strip() for p in phrases_str.split(",") if p.strip()]
        if not phrases:
            return df_to_filter

        try:
            if "ANY" in mode:
                # --- OR LOGIC ---
                regex_pattern = "|".join(phrases)
                filtered_df = df_to_filter[
                    df_to_filter["Details"].astype(str).str.contains(regex_pattern, case=False, na=False)
                ]
            else:
                # --- AND LOGIC ---
                # Construct a lookaround pattern: (?=.*IIT)(?=.*NEFT)
                regex_pattern = "".join([f"(?=.*{p})" for p in phrases])
                filtered_df = df_to_filter[
                    df_to_filter["Details"].astype(str).str.contains(regex_pattern, case=False, na=False)
                ]

            # (Keep the rest of your summary metrics and return statements down here...)
            if filtered_df.empty:
                st.warning("No transactions matched your search parameters.")
                return filtered_df
            
                            # Calculate metrics for the matches
            debit_value = filtered_df["Debit"].sum()
            # Clean currency format mapping
            credit_value = filtered_df["Credit"].sum()

            # Display performance scorecard
            st.markdown("#### 📊 Search Summary Results")
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            # Dynamic timeframe formatting
            fmt_start = filtered_df["Date"].dt.strftime("%d %b %Y").iloc[0]
            fmt_end = filtered_df["Date"].dt.strftime("%d %b %Y").iloc[-1]
            metric_col1.markdown(f"**Active Time Frame:**\n`{fmt_start} to {fmt_end}`")

            metric_col2.metric(
                label="Total Debited (Spent)",
                value=f"₹{debit_value:,.2f}",
                delta="- Expenses",
                delta_color="inverse",
            )
            metric_col3.metric(
                label="Total Credited (Earned)",
                value=f"₹{credit_value:,.2f}",
                delta="+ Earnings",
            )

            return filtered_df
                

        except Exception as e:
            st.error(f"Search Error: {e}")
            return df_to_filter

    # 3. Call the updated function passing the active mode layout parameter
    results_df = filter_search(selected_data, search_query, search_mode)

    if not results_df.empty:
        st.markdown(f"**Found {len(results_df)} matching entries:**")
        st.dataframe(results_df, width='stretch')

    ## Top Credits and debits in the filtered results
    st.markdown("---")
    # spinbox to enter number of top transactions to show
    num_top_transactions = st.number_input(
        "Number of Top Transactions to Show:",
        min_value=1,
        max_value=100,
        value=5
    )

    if not results_df.empty:
        st.markdown("#### 💡 Top Transactions in Filtered Results")
        top_debits = results_df.sort_values(by="Debit", ascending=False).head(num_top_transactions)
        top_credits = results_df.sort_values(by="Credit", ascending=False).head(num_top_transactions)

        st.markdown("**Top Debits (Expenses)**")
        st.dataframe(top_debits[["Date", "Details", "Debit"]], width='stretch')
        st.markdown("**Top Credits (Earnings)**")
        st.dataframe(top_credits[["Date", "Details", "Credit"]], width='stretch')
    st.markdown("---")

else:
    st.warning("Please upload an Excel file and enter the password in the sidebar to begin.")





