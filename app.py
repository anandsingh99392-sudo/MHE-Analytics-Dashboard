import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import io

# Page config
st.set_page_config(page_title="MHE Analytics Dashboard", page_icon="🏭", layout="wide")

# --- SESSION STATE INIT ---
if "equipment_df" not in st.session_state:
    st.session_state.equipment_df = pd.DataFrame()
if "trend_df" not in st.session_state:
    st.session_state.trend_df = pd.DataFrame()
if "summary_df" not in st.session_state:
    st.session_state.summary_df = pd.DataFrame()

# --- DATA UPLOAD SECTION ---
st.sidebar.header("📂 Upload Datasets")
uploaded_eq = st.sidebar.file_uploader("Equipment Master Data (CSV/Excel)", type=["csv", "xlsx"])
uploaded_trend = st.sidebar.file_uploader("Monthly Trend Data (CSV/Excel)", type=["csv", "xlsx"])
uploaded_summary = st.sidebar.file_uploader("Summary Statistics (CSV/Excel)", type=["csv", "xlsx"])

def load_dataframe(uploaded_file):
    if uploaded_file is None:
        return pd.DataFrame()
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

if uploaded_eq:
    st.session_state.equipment_df = load_dataframe(uploaded_eq)
if uploaded_trend:
    st.session_state.trend_df = load_dataframe(uploaded_trend)
if uploaded_summary:
    st.session_state.summary_df = load_dataframe(uploaded_summary)

# --- USE SAMPLE DATA IF NOTHING UPLOADED ---
@st.cache_data
def load_sample_data():
    # (Insert the full raw_data string and extraction logic from your original code here)
    # For brevity, we'll return empty DataFrames if not uploaded — replace with your sample loader if desired.
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

if st.session_state.equipment_df.empty:
    st.session_state.equipment_df, st.session_state.trend_df, st.session_state.summary_df = load_sample_data()

# --- SIDEBAR: EDIT CATEGORIES & THRESHOLDS ---
st.sidebar.header("🔧 Dashboard Settings")
utilization_threshold = st.sidebar.slider("Utilization Target (%)", 50, 95, 75)
mtbf_threshold = st.sidebar.slider("MTBF Target (hrs)", 200, 800, 400)
mttr_threshold = st.sidebar.slider("MTTR Target (hrs)", 1.0, 10.0, 3.0, step=0.5)

# --- MAIN HEADER ---
st.title("🏭 MHE Equipment Analytics Dashboard")
st.caption("Upload your data or use sample data → Edit inline → Visualize → Export")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview", "🏗️ Equipment", "⚠️ Failures & Maintenance", "📊 Custom Analysis"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    if not st.session_state.equipment_df.empty:
        eq_df = st.session_state.equipment_df
        # KPI Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Equipment", len(eq_df))
        c2.metric("Avg Utilization", f"{eq_df['Utilization_Percentage'].mean():.1f}%")
        c3.metric("Avg MTBF", f"{eq_df['MTBF_Hours'].mean():.1f} hrs")
        c4.metric("Avg MTTR", f"{eq_df['MTTR_Hours'].mean():.1f} hrs")

        # Charts
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Utilization by Type")
            summary = eq_df.groupby("Equipment_Type")["Utilization_Percentage"].mean().reset_index()
            fig = px.bar(summary, x="Equipment_Type", y="Utilization_Percentage", color="Equipment_Type",
                         title="Average Utilization (%)")
            fig.add_hline(y=utilization_threshold, line_dash="dash", annotation_text=f"Target: {utilization_threshold}%")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Failures by Type")
            if "Total_Failures" in eq_df.columns:
                failures = eq_df.groupby("Equipment_Type")["Total_Failures"].sum().reset_index()
                fig = px.pie(failures, values="Total_Failures", names="Equipment_Type", title="Total Failures Distribution")
                st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: EQUIPMENT DETAILS (EDITABLE) ---
with tab2:
    st.subheader("✏️ Equipment Master Data (Editable)")
    if not st.session_state.equipment_df.empty:
        edited_eq = st.data_editor(
            st.session_state.equipment_df,
            num_rows="dynamic",
            use_container_width=True,
            key="equipment_editor"
        )
        st.session_state.equipment_df = edited_eq  # auto-update session state

        # Category Management
        st.markdown("#### 🔁 Manage Categories")
        cat_col1, cat_col2 = st.columns(2)
        with cat_col1:
            new_type = st.text_input("Add New Equipment Type")
            if st.button("Add Type") and new_type:
                # Add dummy row for new type (you can expand this logic)
                new_row = pd.DataFrame([{
                    "Equipment_ID": f"NEW-{new_type[:3].upper()}-001",
                    "Equipment_Type": new_type,
                    "Equipment_Name": "New Equipment",
                    "Location": "TBD",
                    "Department": "Operations",
                    "Utilization_Percentage": 0,
                    "Total_Failures": 0,
                    "MTBF_Hours": 0,
                    "MTTR_Hours": 0,
                    "Status": "Operational",
                    "Criticality": "Medium"
                }])
                st.session_state.equipment_df = pd.concat([st.session_state.equipment_df, new_row], ignore_index=True)
                st.success(f"Added new type: {new_type}")
                st.rerun()

        with cat_col2:
            if st.button("Remove Selected Types"):
                # (Optional: add multiselect to choose types to delete)
                st.warning("Feature: Select types to remove (implement with multiselect for full control).")

# --- TAB 3: FAILURES & MAINTENANCE ---
with tab3:
    st.subheader("🔧 Maintenance & Failure Records")
    if not st.session_state.trend_df.empty:
        st.data_editor(st.session_state.trend_df, num_rows="dynamic", use_container_width=True, key="trend_editor")

# --- TAB 4: CUSTOM ANALYSIS ---
with tab4:
    st.subheader("📊 Custom Filters & Insights")
    if not st.session_state.equipment_df.empty:
        # Filter by thresholds
        filtered = st.session_state.equipment_df[
            (st.session_state.equipment_df["Utilization_Percentage"] < utilization_threshold) |
            (st.session_state.equipment_df["MTBF_Hours"] < mtbf_threshold) |
            (st.session_state.equipment_df["MTTR_Hours"] > mttr_threshold)
        ]
        st.markdown(f"#### 🚨 Equipment Below Targets ({len(filtered)} units)")
        st.dataframe(filtered, use_container_width=True)

        # Export button
        if st.button("📥 Export Modified Equipment Data as CSV"):
            csv = st.session_state.equipment_df.to_csv(index=False)
            st.download_button("Download CSV", csv, "modified_equipment_data.csv", "text/csv")

# --- FOOTER ---
st.markdown("---")
st.caption("Edit → Visualize → Export. All changes reflect instantly. Upload your own CSV/Excel to start!")
