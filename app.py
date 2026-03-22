import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import sys

# Configure page
st.set_page_config(
    page_title="MHE Equipment Analytics Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data function
@st.cache_data
def load_data():
    raw_data = '''# MHE COMPLETE DATASET FOR AI-GENERATED REPORT
# Equipment Types: Boom Lift, Transporter, EoT Crane, Hydra, Trailer, Fork Lift, Scissor Lift
# Metrics: Utilization, MTTR (Mean Time To Repair), MTBF (Mean Time Between Failures)

#####################################
# SECTION 1: EQUIPMENT MASTER DATA
#####################################
Equipment_ID,Equipment_Type,Equipment_Name,Location,Department,Purchase_Date,Last_Maintenance_Date,Operating_Hours_Total,Operating_Hours_Month,Available_Hours_Month,Utilization_Percentage,Total_Failures,Total_Downtime_Hours,MTBF_Hours,MTTR_Hours,Status,Criticality,Operator_ID,Maintenance_Cost_YTD,Next_Scheduled_Maintenance
BL-001,Boom Lift,JLG 600S,Warehouse A,Operations,2020-03-15,2024-01-10,4520,180,240,75.0,12,48,376.67,4.0,Operational,High,OP-101,12500,2024-02-15
BL-002,Boom Lift,Genie S-65,Warehouse B,Operations,2021-06-20,2024-01-05,3200,165,240,68.75,8,28,400.0,3.5,Operational,High,OP-102,8900,2024-02-20
BL-003,Boom Lift,JLG 450AJ,Construction Site C,Projects,2019-08-10,2023-12-28,5800,200,240,83.33,15,67.5,386.67,4.5,Under Maintenance,Critical,OP-103,18200,2024-01-30
TR-001,Transporter,Combilift C4000,Warehouse A,Logistics,2020-11-25,2024-01-12,3800,175,240,72.92,10,35,380.0,3.5,Operational,High,OP-104,9800,2024-02-18
TR-002,Transporter,Jungheinrich ETV 216,Warehouse B,Logistics,2022-02-14,2024-01-08,2100,155,240,64.58,5,15,420.0,3.0,Operational,Medium,OP-105,5200,2024-02-25
TR-003,Transporter,Crown TSP 6000,Distribution Center,Logistics,2021-09-30,2023-12-20,2900,190,240,79.17,7,24.5,414.29,3.5,Operational,High,OP-106,7100,2024-02-10
EOT-001,EoT Crane,Konecranes 10T,Manufacturing Plant,Production,2018-04-05,2024-01-15,8500,210,240,87.5,18,90,472.22,5.0,Operational,Critical,OP-107,25600,2024-02-28
EOT-002,EoT Crane,Demag 15T,Assembly Line,Production,2019-01-20,2024-01-02,7200,195,240,81.25,14,63,514.29,4.5,Operational,Critical,OP-108,21300,2024-02-15
EOT-003,EoT Crane,Street Crane 8T,Warehouse A,Operations,2020-07-12,2023-12-15,5100,170,240,70.83,11,44,463.64,4.0,Under Maintenance,High,OP-109,14800,2024-01-25
HY-001,Hydra,ACE 14T,Construction Site A,Projects,2021-03-08,2024-01-10,3400,185,240,77.08,9,40.5,377.78,4.5,Operational,High,OP-110,11200,2024-02-20
HY-002,Hydra,Action 12T,Construction Site B,Projects,2020-09-15,2024-01-05,4100,195,240,81.25,11,49.5,372.73,4.5,Operational,High,OP-111,13500,2024-02-12
HY-003,Hydra,Escorts 10T,Warehouse C,Operations,2022-05-22,2023-12-28,2200,160,240,66.67,6,21,366.67,3.5,Operational,Medium,OP-112,6800,2024-02-28
TL-001,Trailer,Utility 40ft,Distribution Center,Logistics,2019-06-10,2024-01-08,6200,200,240,83.33,8,24,775.0,3.0,Operational,Medium,OP-113,8500,2024-03-01
TL-002,Location/Warehouse A,Operations,2020-02-28,2024-01-15,4900,195,240,81.25,14,42,350.0,3.0,Operational,High,OP-116,10200,2024-02-18
SL-001,Scissor Lift,JLG 3246ES,Warehouse A,Maintenance,2021-02-20,2024-01-12,3100,150,240,62.5,8,20,387.5,2.5,Operational,Medium,OP-120,6400,2024-02-20
SL-002,Scissor Lift,Genie GS-2632,Warehouse B,Maintenance,2020-08-14,2024-01-05,3800,160,240,66.67,9,22.5,422.22,2.5,Operational,Medium,OP-121,7200,2024-02-15
SL-003,Scissor Lift,Skyjack SJIII 4632,Manufacturing Plant,Maintenance,2022-06-30,2023-12-20,1800,140,240,58.33,5,10,360.0,2.0,Operational,Low,OP-122,3800,2024-03-05
SL-004,Scissor Lift,Haulotte Compact 12,Assembly Line,Production,2021-10-25,2024-01-08,2600,155,240,64.58,7,14,371.43,2.0,Operational,Medium,OP-123,5100,2024-02-25'''

    # Parse data
    lines = raw_data.split('\n')
    
    # Find equipment master data section
    master_data_start = None
    for i, line in enumerate(lines):
        if "SECTION 1: EQUIPMENT MASTER DATA" in line:
            master_data_start = i + 2
            break
    
    if master_data_start:
        # Extract master data lines
        master_lines = []
        i = master_data_start
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
            master_lines.append(lines[i])
            i += 1
        
        # Convert to DataFrame
        if master_lines:
            master_df = pd.read_csv(io.StringIO('\n'.join(master_lines)))
            # Fix column names if needed
            if 'Location/Warehouse A' in master_df.columns:
                master_df = master_df.rename(columns={'Location/Warehouse A': 'Location'})
            
            # Convert date columns
            date_cols = ['Purchase_Date', 'Last_Maintenance_Date', 'Next_Scheduled_Maintenance']
            for col in date_cols:
                if col in master_df.columns:
                    master_df[col] = pd.to_datetime(master_df[col])
            
            return master_df
    
    return pd.DataFrame()

# Load data
equipment_df = load_data()

# Sidebar filters
st.sidebar.title("🔧 Filters")
equipment_types = equipment_df['Equipment_Type'].unique()
selected_types = st.sidebar.multiselect(
    "Select Equipment Types",
    equipment_types,
    default=list(equipment_types)
)

locations = equipment_df['Location'].unique()
selected_locations = st.sidebar.multiselect(
    "Select Locations",
    locations,
    default=list(locations)
)

statuses = equipment_df['Status'].unique()
selected_statuses = st.sidebar.multiselect(
    "Select Status",
    statuses,
    default=list(statuses)
)

# Apply filters
filtered_df = equipment_df[
    (equipment_df['Equipment_Type'].isin(selected_types)) &
    (equipment_df['Location'].isin(selected_locations)) &
    (equipment_df['Status'].isin(selected_statuses))
]

# Main dashboard
st.title("🏭 MHE Equipment Analytics Dashboard")
st.markdown("Real-time monitoring of Material Handling Equipment performance")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Equipment", len(filtered_df))
with col2:
    avg_util = filtered_df['Utilization_Percentage'].mean()
    st.metric("Avg Utilization", f"{avg_util:.1f}%")
with col3:
    total_cost = filtered_df['Maintenance_Cost_YTD'].sum()
    st.metric("Total Cost", f"${total_cost:,}")
with col4:
    under_maintenance = filtered_df[filtered_df['Status'] == 'Under Maintenance'].shape[0]
    st.metric("Under Maintenance", under_maintenance)

# Charts
st.subheader("📊 Performance Analysis")
tab1, tab2, tab3 = st.tabs(["Utilization", "Cost Analysis", "Equipment Details"])

with tab1:
    # Utilization chart
    util_by_type = filtered_df.groupby('Equipment_Type')['Utilization_Percentage'].mean().reset_index()
    fig = px.bar(
        util_by_type,
        x='Equipment_Type',
        y='Utilization_Percentage',
        title='Average Utilization by Equipment Type',
        color='Utilization_Percentage'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performers
    top_util = filtered_df.nlargest(5, 'Utilization_Percentage')
    fig2 = px.bar(
        top_util,
        x='Equipment_ID',
        y='Utilization_Percentage',
        title='Top 5 Equipment by Utilization',
        color='Equipment_Type'
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    # Cost analysis
    cost_by_type = filtered_df.groupby('Equipment_Type')['Maintenance_Cost_YTD'].sum().reset_index()
    fig3 = px.bar(
        cost_by_type,
        x='Equipment_Type',
        y='Maintenance_Cost_YTD',
        title='Maintenance Cost by Equipment Type',
        color='Maintenance_Cost_YTD'
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Cost vs Utilization
    fig4 = px.scatter(
        filtered_df,
        x='Utilization_Percentage',
        y='Maintenance_Cost_YTD',
        size='Operating_Hours_Total',
        color='Equipment_Type',
        hover_name='Equipment_ID',
        title='Cost vs Utilization Analysis'
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab3:
    # Equipment details table
    st.dataframe(
        filtered_df,
        column_config={
            "Purchase_Date": st.column_config.DateColumn("Purchase Date"),
            "Last_Maintenance_Date": st.column_config.DateColumn("Last Maintenance"),
            "Next_Scheduled_Maintenance": st.column_config.DateColumn("Next Maintenance"),
            "Maintenance_Cost_YTD": st.column_config.NumberColumn("Maintenance Cost", format="$%d")
        },
        use_container_width=True,
        height=400
    )
    
    # Export data
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        "📥 Download Filtered Data",
        csv_data,
        file_name="mhe_equipment_data.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption("© 2026 MHE Analytics Dashboard | Version 1.0")
