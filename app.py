import io
import msoffcrypto
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Account Statement Dashboard",
    page_icon="🏦",
    layout="wide"
)

# Set up the title of the web page
st.title("🏦 Account Statement Dashboard")
st.markdown("Upload your encrypted Excel statement to visualize your financial trends.")


# --- 1. CORE PERFORMANCE FIX: ADDING CACHING ---
# This ensures that decryption and dataframe building happen ONLY when the files or password change!
@st.cache_data(show_spinner="Decrypting and compiling statements...")
def process_multiple_statements(uploaded_files, password=None):
    all_dfs = []
    
    for uploaded_file in uploaded_files:
        try:
            # Create a copy of the bytes to prevent buffer read position issues
            file_bytes = io.BytesIO(uploaded_file.getvalue())
            decrypted = io.BytesIO()
            
            file = msoffcrypto.OfficeFile(file_bytes)
            if file.is_encrypted():
                if not password:
                    return f"⚠️ '{uploaded_file.name}' is password-protected. Please enter the password in the sidebar."
                
                file.load_key(password=password)
                file.decrypt(decrypted)
                decrypted.seek(0)  # Reset buffer position after decryption

                # Standard layout parsing based on your template layout
                df = pd.read_excel(decrypted, skiprows=17, skipfooter=8)
            else:
                # If the file is not encrypted, read directly from the uploaded file
                file_bytes.seek(0)  # Ensure buffer is at the start
                df = pd.read_excel(uploaded_file, skiprows=17, skipfooter=8)

            df.columns = df.columns.str.strip()
            
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=["Date"])
                all_dfs.append(df)
                
        except Exception as e:
            # In cached functions, it is safer to raise or return None rather than call sidebar widgets directly
            return f"Error decrypting {uploaded_file.name}: {str(e)}"

    if not all_dfs:
        return None

    # Concatenate all parsed files into a single master layout
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Clean up metric numeric conversions before checking for row equality
    for col in ["Balance", "Debit", "Credit"]:
        if col in combined_df.columns:
            if combined_df[col].dtype == "object":
                combined_df[col] = combined_df[col].astype(str).str.replace(",", "").str.strip()
            combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce")
            combined_df[col] = combined_df[col].fillna(0)

    # Chronological sort so timeline sequences correctly
    combined_df = combined_df.sort_values(by="Date").reset_index(drop=True)
    
    # Drops identical overlapping lines while keeping the original single source records
    combined_df = combined_df.drop_duplicates(
        subset=["Date", "Details", "Debit", "Credit", "Balance"], 
        keep="first"
    ).reset_index(drop=True)

    return combined_df


# --- STREAMLIT SIDEBAR / INTERFACE CONTROLS ---
st.sidebar.header("Settings")

uploaded_files = st.sidebar.file_uploader(
    "Select your account statement(s)", 
    type=["xls", "xlsx"],
    accept_multiple_files=True
)

password = st.sidebar.text_input("Enter Statement Password", type="password")
st.sidebar.markdown("---")


# --- MAIN PAGE LOGIC ---
if uploaded_files:

    # Run your optimized cached processing logic
    data_output = process_multiple_statements(uploaded_files, password)

    # Error handling boundary if caching returned a string error
    if isinstance(data_output, str):
        st.error(data_output)
    elif data_output is not None and not data_output.empty:
        df = data_output

        # Clean remaining data states and sort chronologically
        df["Debit"] = df["Debit"].fillna(0)
        df["Credit"] = df["Credit"].fillna(0)
        df = df.dropna(subset=["Date"]).sort_values(by="Date").reset_index(drop=True)

        # Date range variables for chart titles
        if not df["Date"].isnull().all():
            min_date = df["Date"].min().to_pydatetime()
            max_date = df["Date"].max().to_pydatetime()

            # Create a range slider where the user sweeps across timestamps
            selected_date_range = st.slider(
                "Select Date Range to Analyze:",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="DD MMM YYYY",
            )

            # Filter the primary dataframe based on the slider bounds
            slider_start, slider_end = selected_date_range
            selected_data = df[df["Date"].between(slider_start, slider_end)].reset_index(drop=True) # CRITICAL FIX: Reset Index!

            start_date_str = slider_start.strftime("%d %b %Y")
            end_date_str = slider_end.strftime("%d %b %Y")
        else:
            selected_data = df.copy()
            start_date_str = df["Date"].dt.strftime("%d %b %Y").iloc[0] if not df.empty else ""
            end_date_str = df["Date"].dt.strftime("%d %b %Y").iloc[-1] if not df.empty else ""

        # 1. Build the clean baseline chart
        fig_combined = px.line(
            selected_data,
            x="Date",
            y="Balance",
            title=f"Statement Trends: {start_date_str} - {end_date_str}",
            labels={"Date": "Transaction Date", "Balance": "Account Balance (₹)"},
        )
        
        fig_combined.update_traces(
            mode="lines+markers",
            marker=dict(size=6, color="#55e32a"),
            line=dict(width=2, color="#1f77b4"),
            hoverinfo="skip" 
        )
        
        fig_combined.update_layout(
            xaxis_tickangle=45,
            clickmode="event+select"
        )
        
        fig_combined.update_xaxes(showspikes=True, spikecolor="gray", spikethickness=1, spikemode="across")
        fig_combined.update_yaxes(showspikes=True, spikecolor="gray", spikethickness=1)

        # 2. Render chart with modern width constraints
        event_data = st.plotly_chart(fig_combined, width='stretch', on_select="rerun")

        # 3. INTERACTIVE BOX: Catch click actions safely
        if event_data and "selection" in event_data and "points" in event_data["selection"] and len(event_data["selection"]["points"]) > 0:
            selected_point = event_data["selection"]["points"][0]
            point_index = selected_point["point_index"]
            
            # CRITICAL FIX: Target selected_data, NOT the full df!
            row = selected_data.iloc[point_index]
            
            st.markdown("---")
            st.markdown("### 🔍 Inspected Transaction Details")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("📅 Date", row["Date"].strftime("%d %b %Y"))
            
            if row["Debit"] > 0:
                m2.metric("🛑 Outgoing Debit", f"₹{row['Debit']:,.2f}", delta="- Expenses", delta_color="normal")
            else:
                m2.metric("🛑 Outgoing Debit", "₹0.00")
                
            if row["Credit"] > 0:
                m3.metric("🟢 Incoming Credit", f"₹{row['Credit']:,.2f}", delta="+ Earnings")
            else:
                m3.metric("🟢 Incoming Credit", "₹0.00")
            m4.metric("💰 Running Balance", f"₹{row['Balance']:,.2f}")
            
            st.markdown(f"**Bank Transaction String Description:**\n\n`{row['Details']}`")
        else:
            st.info("👆 Click on any milestone coordinate dot on the chart timeline above to populate the specific transaction details here.")


        ## Top Credits and debits section Logic -------
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        col1.markdown(
            f"### <span style='color: #FF5733;'>Top Transactions during:</span> {start_date_str} - {end_date_str}", 
            unsafe_allow_html=True
        )
        num_top_transactions = col2.number_input(
            "Number of Top Transactions to Show:",
            min_value=1,
            max_value=100,
            value=5
        )

        # Use results_df if a search query exists, otherwise fall back to selected_data range
        source_df = selected_data.copy()

        if source_df is not None and not source_df.empty:
            top_debits = source_df.sort_values(by="Debit", ascending=False).head(num_top_transactions)
            top_credits = source_df.sort_values(by="Credit", ascending=False).head(num_top_transactions)

            st.markdown("**Top Debits (Expenses)**")
            st.dataframe(top_debits[["Date", "Details", "Debit"]], width='stretch')
            st.markdown("**Top Credits (Earnings)**")
            st.dataframe(top_credits[["Date", "Details", "Credit"]], width='stretch')


        # --- Filtering Logic Start ---
        st.markdown("---")
        st.subheader("🔍 Advanced Transaction Search & Filtering")

        search_query = st.text_input(
            "Enter filter words / phrases (separate multiple words with commas):",
            placeholder="e.g., ZERODHA, SWIGGY, NEFT, UPI, AMAZON",
        ).strip()

        search_mode = st.radio(
            "Search Mode:",
            options=["Match ANY word (OR)", "Match ALL words (AND)"],
            horizontal=True
        )

        # Defining search logic inside execution layout scope securely
        def filter_search(df_to_filter, phrases_str, mode):
            if not phrases_str:
                return df_to_filter

            phrases = [p.strip() for p in phrases_str.split(",") if p.strip()]
            if not phrases:
                return df_to_filter

            try:
                if "ANY" in mode:
                    regex_pattern = "|".join(phrases)
                    filtered_df = df_to_filter[
                        df_to_filter["Details"].astype(str).str.contains(regex_pattern, case=False, na=False)
                    ]
                else:
                    regex_pattern = "".join([f"(?=.*{p})" for p in phrases])
                    filtered_df = df_to_filter[
                        df_to_filter["Details"].astype(str).str.contains(regex_pattern, case=False, na=False)
                    ]

                if filtered_df.empty:
                    st.warning("No transactions matched your search parameters.")
                    return filtered_df
                
                debit_value = filtered_df["Debit"].sum()
                credit_value = filtered_df["Credit"].sum()

                fmt_start = filtered_df["Date"].dt.strftime("%d %b %Y").iloc[0]
                fmt_end = filtered_df["Date"].dt.strftime("%d %b %Y").iloc[-1]
                
                col1, col2 = st.columns([2, 1])
                col1.markdown("#### 📊 Search Summary Results")
                col2.markdown(f"**Active Time Frame:**\n`{fmt_start} to {fmt_end}`")
                metric_col1, metric_col2 = st.columns(2)

                metric_col1.metric(
                    label="Total Debited (Spent)",
                    value=f"₹{debit_value:,.2f}",
                    delta="- Expenses",
                    delta_color="normal",
                )
                metric_col2.metric(
                    label="Total Credited (Earned)",
                    value=f"₹{credit_value:,.2f}",
                    delta="+ Earnings",
                )

                return filtered_df

            except Exception as e:
                st.error(f"Search Error: {e}")
                return df_to_filter

        results_df = filter_search(selected_data, search_query, search_mode)

        if results_df is not None and not results_df.empty and search_query:
            st.markdown(f"**Found {len(results_df)} matching entries:**")
            st.dataframe(results_df, width='stretch')


        st.markdown("---")

        # Show raw Data Table underneath
        with st.expander("🔍 View Raw Transaction Data Table"):
            st.dataframe(df, width='stretch')
else:
    st.warning("Please upload an Excel file and enter the password in the sidebar to begin.")