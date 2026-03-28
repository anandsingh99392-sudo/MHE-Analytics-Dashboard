"""
MHE Equipment Analytics Dashboard
An Interactive Streamlit Application for Material Handling Equipment Monitoring
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="MHE Equipment Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card-red {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .metric-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 15px 30px;
        border-radius: 10px 10px 0 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    .status-operational { background-color: #10B981; color: white; padding: 5px 15px; border-radius: 20px; }
    .status-maintenance { background-color: #F59E0B; color: white; padding: 5px 15px; border-radius: 20px; }
    .status-critical { background-color: #EF4444; color: white; padding: 5px 15px; border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# Data Loading Function
@st.cache_data
def load_all_data():
    """Load and process all MHE equipment data"""
    
    # Equipment Master Data
    equipment_master_data = {
        'Equipment_ID': ['BL-001', 'BL-002', 'BL-003', 'TR-001', 'TR-002', 'TR-003',
                        'EOT-001', 'EOT-002', 'EOT-003', 'HY-001', 'HY-002', 'HY-003',
                        'TL-001', 'TL-002', 'TL-003', 'FL-001', 'FL-002', 'FL-003', 'FL-004',
                        'SL-001', 'SL-002', 'SL-003', 'SL-004'],
        'Equipment_Type': ['Boom Lift', 'Boom Lift', 'Boom Lift',
                          'Transporter', 'Transporter', 'Transporter',
                          'EoT Crane', 'EoT Crane', 'EoT Crane',
                          'Hydra', 'Hydra', 'Hydra',
                          'Trailer', 'Trailer', 'Trailer',
                          'Fork Lift', 'Fork Lift', 'Fork Lift', 'Fork Lift',
                          'Scissor Lift', 'Scissor Lift', 'Scissor Lift', 'Scissor Lift'],
        'Equipment_Name': ['JLG 600S', 'Genie S-65', 'JLG 450AJ',
                          'Combilift C4000', 'Jungheinrich ETV 216', 'Crown TSP 6000',
                          'Konecranes 10T', 'Demag 15T', 'Street Crane 8T',
                          'ACE 14T', 'Action 12T', 'Escorts 10T',
                          'Utility 40ft', 'Flatbed 48ft', 'Lowboy 53ft',
                          'Toyota 8FGU25', 'Hyster H50FT', 'Crown FC 5200', 'Yale GLP050VX',
                          'JLG 3246ES', 'Genie GS-2632', 'Skyjack SJIII 4632', 'Haulotte Compact 12'],
        'Location': ['Warehouse A', 'Warehouse B', 'Construction Site C',
                    'Warehouse A', 'Warehouse B', 'Distribution Center',
                    'Manufacturing Plant', 'Assembly Line', 'Warehouse A',
                    'Construction Site A', 'Construction Site B', 'Warehouse C',
                    'Distribution Center', 'Warehouse A', 'Construction Site A',
                    'Warehouse A', 'Warehouse B', 'Distribution Center', 'Manufacturing Plant',
                    'Warehouse A', 'Warehouse B', 'Manufacturing Plant', 'Assembly Line'],
        'Department': ['Operations', 'Operations', 'Projects',
                     'Logistics', 'Logistics', 'Logistics',
                     'Production', 'Production', 'Operations',
                     'Projects', 'Projects', 'Operations',
                     'Logistics', 'Logistics', 'Projects',
                     'Operations', 'Operations', 'Logistics', 'Production',
                     'Maintenance', 'Maintenance', 'Maintenance', 'Production'],
        'Utilization_Percentage': [75.0, 68.75, 83.33, 72.92, 64.58, 79.17,
                                   87.5, 81.25, 70.83, 77.08, 81.25, 66.67,
                                   83.33, 77.08, 72.92, 81.25, 75.0, 83.33, 68.75,
                                   62.5, 66.67, 58.33, 64.58],
        'MTBF_Hours': [376.67, 400.0, 386.67, 380.0, 420.0, 414.29,
                      472.22, 514.29, 463.64, 377.78, 372.73, 366.67,
                      775.0, 800.0, 620.0, 350.0, 360.0, 343.75, 342.86,
                      387.5, 422.22, 360.0, 371.43],
        'MTTR_Hours': [4.0, 3.5, 4.5, 3.5, 3.0, 3.5,
                      5.0, 4.5, 4.0, 4.5, 4.5, 3.5,
                      3.0, 2.5, 2.5, 3.0, 3.0, 3.5, 3.0,
                      2.5, 2.5, 2.0, 2.0],
        'Total_Failures': [12, 8, 15, 10, 5, 7, 18, 14, 11, 9, 11, 6,
                          8, 6, 5, 14, 10, 16, 7, 8, 9, 5, 7],
        'Status': ['Operational', 'Operational', 'Under Maintenance',
                  'Operational', 'Operational', 'Operational',
                  'Operational', 'Operational', 'Under Maintenance',
                  'Operational', 'Operational', 'Operational',
                  'Operational', 'Operational', 'Operational',
                  'Operational', 'Operational', 'Under Maintenance', 'Operational',
                  'Operational', 'Operational', 'Operational', 'Operational'],
        'Criticality': ['High', 'High', 'Critical',
                       'High', 'Medium', 'High',
                       'Critical', 'Critical', 'High',
                       'High', 'High', 'Medium',
                       'Medium', 'Medium', 'Low',
                       'High', 'High', 'Critical', 'Medium',
                       'Medium', 'Medium', 'Low', 'Medium'],
        'Maintenance_Cost_YTD': [12500, 8900, 18200, 9800, 5200, 7100,
                               25600, 21300, 14800, 11200, 13500, 6800,
                               8500, 6200, 4800, 10200, 7800, 14500, 5600,
                               6400, 7200, 3800, 5100],
        'Operating_Hours_Total': [4520, 3200, 5800, 3800, 2100, 2900,
                                 8500, 7200, 5100, 3400, 4100, 2200,
                                 6200, 4800, 3100, 4900, 3600, 5500, 2400,
                                 3100, 3800, 1800, 2600]
    }
    
    equipment_master_df = pd.DataFrame(equipment_master_data)
    
    # Summary Statistics
    summary_stats_data = {
        'Equipment_Type': ['Boom Lift', 'Transporter', 'EoT Crane', 'Hydra', 
                          'Trailer', 'Fork Lift', 'Scissor Lift', 'TOTAL'],
        'Total_Units': [3, 3, 3, 3, 3, 4, 4, 23],
        'Avg_Utilization_Pct': [75.69, 72.22, 79.86, 75.0, 77.78, 77.08, 62.92, 74.36],
        'Total_Operating_Hours': [13520, 8800, 20800, 9700, 14100, 16400, 11300, 94620],
        'Total_Failures': [35, 22, 43, 26, 19, 47, 29, 221],
        'Total_Downtime_Hours': [143.5, 74.5, 197, 111, 51.5, 149, 66.5, 793.5],
        'Avg_MTBF_Hours': [387.78, 404.76, 483.38, 372.39, 731.67, 349.15, 385.29, 416.35],
        'Avg_MTTR_Hours': [4.0, 3.33, 4.5, 4.17, 2.67, 3.13, 2.25, 3.44],
        'Total_Maintenance_Cost_YTD': [39600, 22100, 61700, 31500, 19500, 38100, 22500, 235000],
        'Units_Under_Maintenance': [1, 0, 1, 0, 0, 1, 0, 3],
        'Critical_Units': [1, 0, 2, 0, 0, 1, 0, 4]
    }
    
    summary_stats_df = pd.DataFrame(summary_stats_data)
    
    # Failure Analysis Data
    failure_data = {
        'Failure_ID': [f'F-{str(i).zfill(3)}' for i in range(1, 31)],
        'Equipment_ID': ['BL-001', 'BL-002', 'BL-003', 'EOT-001', 'EOT-002', 'EOT-003',
                        'FL-001', 'FL-002', 'FL-003', 'HY-001', 'HY-002', 'TR-001',
                        'TR-002', 'SL-001', 'SL-002', 'TL-001', 'TL-002', 'BL-001',
                        'EOT-001', 'FL-001', 'HY-003', 'TR-003', 'SL-003', 'SL-004',
                        'TL-003', 'FL-004', 'EOT-003', 'BL-002', 'HY-001', 'FL-002'],
        'Equipment_Type': ['Boom Lift', 'Boom Lift', 'Boom Lift', 'EoT Crane', 'EoT Crane', 'EoT Crane',
                          'Fork Lift', 'Fork Lift', 'Fork Lift', 'Hydra', 'Hydra', 'Transporter',
                          'Transporter', 'Scissor Lift', 'Scissor Lift', 'Trailer', 'Trailer', 'Boom Lift',
                          'EoT Crane', 'Fork Lift', 'Hydra', 'Transporter', 'Scissor Lift', 'Scissor Lift',
                          'Trailer', 'Fork Lift', 'EoT Crane', 'Boom Lift', 'Hydra', 'Fork Lift'],
        'Failure_Date': pd.to_datetime([
            '2024-01-08', '2024-01-03', '2024-01-15', '2024-01-12', '2024-01-02', '2023-12-28',
            '2024-01-10', '2024-01-08', '2024-01-18', '2024-01-05', '2024-01-02', '2024-01-10',
            '2024-01-06', '2024-01-08', '2024-01-03', '2024-01-05', '2024-01-10', '2023-12-15',
            '2023-12-20', '2023-12-22', '2023-12-18', '2023-12-15', '2023-12-10', '2023-12-05',
            '2023-12-08', '2023-12-12', '2023-12-05', '2023-12-01', '2023-11-28', '2023-11-25'
        ]),
        'Failure_Type': ['Hydraulic Leak', 'Engine Issue', 'Boom Extension Failure', 'Hoist Motor Overheating',
                        'Brake System Failure', 'Trolley Wheel Damage', 'Mast Chain Stretch', 'Transmission Slip',
                        'Battery Failure', 'Outrigger Malfunction', 'Slew Ring Noise', 'Steering Issue',
                        'Load Sensor Error', 'Platform Tilt', 'Scissor Arm Noise', 'Brake Light Failure',
                        'Tire Blowout', 'Platform Control Issue', 'Limit Switch Failure', 'Fork Tilt Cylinder Leak',
                        'Boom Cylinder Leak', 'Drive Motor Issue', 'Platform Lock Failure', 'Control Panel Error',
                        'Coupling Damage', 'Hydraulic Pump Noise', 'Pendant Control Failure', 'Tire Puncture',
                        'Winch Brake Slip', 'Side Shift Malfunction'],
        'Root_Cause': ['Worn Seal', 'Fuel Filter Clog', 'Hydraulic Valve Malfunction', 'Bearing Wear',
                       'Brake Pad Wear', 'Excessive Load', 'Normal Wear', 'Low Fluid Level',
                       'Cell Degradation', 'Hydraulic Cylinder Leak', 'Bearing Wear', 'Power Steering Pump',
                       'Sensor Calibration', 'Leveling Sensor', 'Lubrication Issue', 'Wiring Issue',
                       'Road Hazard', 'Joystick Malfunction', 'Electrical Fault', 'Seal Wear',
                       'Seal Degradation', 'Brush Wear', 'Mechanical Wear', 'Circuit Board Fault',
                       'Impact Damage', 'Pump Wear', 'Cable Damage', 'Road Debris',
                       'Brake Lining Wear', 'Hydraulic Valve'],
        'Downtime_Hours': [4.0, 3.5, 6.0, 5.0, 4.5, 4.0, 3.0, 3.0, 3.5, 4.5, 4.5, 3.5,
                          3.0, 2.5, 2.5, 3.0, 2.5, 4.0, 5.0, 3.0, 3.5, 3.5, 2.0, 2.0,
                          2.5, 3.0, 4.0, 3.5, 4.5, 3.0],
        'Repair_Cost': [850, 420, 1800, 2200, 1100, 950, 650, 380, 2800, 1200, 1800, 750,
                       280, 350, 180, 220, 450, 680, 420, 520, 980, 620, 280, 450,
                       380, 1200, 550, 320, 890, 720],
        'Priority': ['High', 'Medium', 'Critical', 'Critical', 'Critical', 'High',
                    'High', 'Medium', 'High', 'High', 'High', 'Medium',
                    'Low', 'Medium', 'Low', 'Medium', 'Medium', 'High',
                    'Critical', 'Medium', 'High', 'Medium', 'Medium', 'Medium',
                    'Low', 'High', 'High', 'Low', 'High', 'Medium']
    }
    
    failure_df = pd.DataFrame(failure_data)
    
    # Maintenance Schedule Data
    maintenance_data = {
        'Equipment_ID': ['BL-001', 'BL-002', 'BL-003', 'TR-001', 'TR-002', 'TR-003',
                        'EOT-001', 'EOT-002', 'EOT-003', 'HY-001', 'HY-002', 'HY-003',
                        'TL-001', 'TL-002', 'TL-003', 'FL-001', 'FL-002', 'FL-003', 'FL-004',
                        'SL-001', 'SL-002', 'SL-003', 'SL-004'],
        'Equipment_Type': ['Boom Lift', 'Boom Lift', 'Boom Lift',
                          'Transporter', 'Transporter', 'Transporter',
                          'EoT Crane', 'EoT Crane', 'EoT Crane',
                          'Hydra', 'Hydra', 'Hydra',
                          'Trailer', 'Trailer', 'Trailer',
                          'Fork Lift', 'Fork Lift', 'Fork Lift', 'Fork Lift',
                          'Scissor Lift', 'Scissor Lift', 'Scissor Lift', 'Scissor Lift'],
        'Maintenance_Type': ['Preventive', 'Preventive', 'Corrective',
                           'Preventive', 'Preventive', 'Preventive',
                           'Preventive', 'Preventive', 'Corrective',
                           'Preventive', 'Preventive', 'Preventive',
                           'Preventive', 'Preventive', 'Preventive',
                           'Preventive', 'Preventive', 'Corrective', 'Preventive',
                           'Preventive', 'Preventive', 'Preventive', 'Preventive'],
        'Scheduled_Date': pd.to_datetime([
            '2024-02-15', '2024-02-20', '2024-01-30', '2024-02-18', '2024-02-25', '2024-02-10',
            '2024-02-28', '2024-02-15', '2024-01-25', '2024-02-20', '2024-02-12', '2024-02-28',
            '2024-03-01', '2024-03-10', '2024-02-25', '2024-02-18', '2024-02-22', '2024-01-28',
            '2024-02-28', '2024-02-20', '2024-02-15', '2024-03-05', '2024-02-25'
        ]),
        'Estimated_Duration_Hours': [4, 4, 8, 3, 3, 3, 6, 6, 8, 5, 5, 4,
                                    2, 2, 2, 3, 3, 6, 3, 2, 2, 2, 2],
        'Estimated_Cost': [800, 800, 2500, 600, 600, 600, 1500, 1500, 2200, 1000, 1000, 800,
                          400, 400, 400, 600, 600, 1800, 600, 400, 400, 400, 400],
        'Priority': ['Medium', 'Medium', 'Critical',
                    'Medium', 'Low', 'Medium',
                    'High', 'High', 'Critical',
                    'High', 'High', 'Medium',
                    'Low', 'Low', 'Low',
                    'High', 'Medium', 'Critical', 'Medium',
                    'Medium', 'Medium', 'Low', 'Medium'],
        'Assigned_Technician': ['TECH-01', 'TECH-02', 'TECH-01', 'TECH-04', 'TECH-06', 'TECH-04',
                                'TECH-03', 'TECH-03', 'TECH-04', 'TECH-02', 'TECH-02', 'TECH-02',
                                'TECH-04', 'TECH-04', 'TECH-04', 'TECH-05', 'TECH-05', 'TECH-06',
                                'TECH-05', 'TECH-01', 'TECH-01', 'TECH-01', 'TECH-06'],
        'Notes': ['Quarterly hydraulic system check', 'Quarterly hydraulic system check',
                 'Boom extension repair completion', 'Battery and drive system check',
                 'Routine inspection', 'Steering system inspection',
                 'Annual load test and inspection', 'Brake system inspection',
                 'Trolley system repair', 'Outrigger and boom inspection',
                 'Slew ring inspection', 'General inspection',
                 'Brake and tire inspection', 'Brake and tire inspection',
                 'Coupling inspection', 'Mast and hydraulic check',
                 'Transmission service', 'Battery system replacement',
                 'General inspection', 'Platform and scissor inspection',
                 'Lubrication and inspection', 'General inspection',
                 'Control system check']
    }
    
    maintenance_df = pd.DataFrame(maintenance_data)
    
    # Operator Performance Data
    operator_data = {
        'Operator_ID': [f'OP-{str(i).zfill(3)}' for i in range(101, 124)],
        'Operator_Name': ['John Smith', 'Sarah Johnson', 'Mike Williams', 'Emily Brown', 'David Lee',
                         'Lisa Chen', 'Robert Taylor', 'Jennifer Martinez', 'James Anderson', 'Maria Garcia',
                         'Thomas Wilson', 'Amanda Moore', 'Christopher Davis', 'Jessica Thompson', 'Daniel Jackson',
                         'Michelle White', 'Kevin Harris', 'Stephanie Clark', 'Brian Lewis', 'Nicole Robinson',
                         'Andrew Walker', 'Rachel Hall', 'Steven Young'],
        'Department': ['Operations', 'Operations', 'Projects', 'Logistics', 'Logistics',
                      'Logistics', 'Production', 'Production', 'Operations', 'Projects',
                      'Projects', 'Operations', 'Logistics', 'Logistics', 'Projects',
                      'Operations', 'Operations', 'Logistics', 'Production', 'Maintenance',
                      'Maintenance', 'Maintenance', 'Production'],
        'Total_Operating_Hours': [1850, 1620, 2100, 1780, 1420, 1950, 2200, 2050, 1680, 1850,
                                  2000, 1550, 1920, 1750, 1600, 1980, 1720, 2100, 1580, 1420,
                                  1580, 1280, 1500],
        'Incidents_Count': [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        'Safety_Score': [98, 92, 96, 97, 95, 91, 99, 98, 90, 96, 97, 94, 95, 96, 93,
                        98, 89, 97, 94, 96, 95, 97, 94],
        'Training_Hours_YTD': [24, 16, 32, 20, 16, 24, 40, 36, 28, 32, 36, 24, 12, 16, 12,
                              24, 20, 28, 20, 16, 20, 12, 18]
    }
    
    operator_df = pd.DataFrame(operator_data)
    
    # Spare Parts Inventory Data
    spare_parts_data = {
        'Part_ID': [f'SP-{str(i).zfill(3)}' for i in range(1, 21)],
        'Part_Name': ['Hydraulic Seal Kit', 'Fuel Filter Assembly', 'Motor Bearings', 'Brake Pads Set',
                     'Trolley Wheels', 'Mast Chains', 'Battery Pack', 'Outrigger Cylinder',
                     'Slew Ring Bearing', 'Power Steering Pump', 'Load Cell Sensor', 'Leveling Sensor',
                     'Wiring Harness', 'Tires - Industrial', 'Joystick Controller', 'Limit Switches',
                     'Cylinder Seals', 'Hydraulic Pump', 'Pendant Cable', 'Coupling Assembly'],
        'Current_Stock': [25, 18, 12, 30, 8, 15, 4, 6, 4, 8, 10, 12, 20, 16, 6, 15, 30, 4, 8, 10],
        'Minimum_Stock': [10, 8, 5, 15, 4, 6, 2, 3, 2, 4, 5, 6, 10, 8, 3, 8, 15, 2, 4, 5],
        'Reorder_Point': [15, 12, 8, 20, 6, 10, 3, 4, 3, 6, 7, 8, 15, 12, 4, 10, 20, 3, 6, 7],
        'Unit_Cost': [85, 42, 180, 95, 220, 145, 2800, 890, 1650, 680, 245, 125, 85, 320, 580, 65, 45, 1150, 185, 340],
        'Lead_Time_Days': [7, 5, 14, 7, 21, 10, 30, 21, 28, 14, 10, 7, 5, 7, 14, 5, 5, 21, 10, 14],
        'Supplier': ['HydraulicParts Inc', 'FilterPro Supply', 'BearingWorld', 'BrakeMaster',
                    'CraneParts Ltd', 'ChainSupply Co', 'PowerCell Inc', 'HydraCylinders',
                    'BearingWorld', 'SteerParts Inc', 'SensorTech', 'SensorTech',
                    'WireWorks', 'TirePro Supply', 'ControlSystems', 'ElectroParts',
                    'SealMaster', 'HydraulicParts Inc', 'CableTech', 'TrailerParts Co']
    }
    
    spare_parts_df = pd.DataFrame(spare_parts_data)
    
    return {
        'equipment_master': equipment_master_df,
        'summary_stats': summary_stats_df,
        'failure_analysis': failure_df,
        'maintenance_schedule': maintenance_df,
        'operator_performance': operator_df,
        'spare_parts': spare_parts_df
    }

# Load all data
data = load_all_data()

# Header
st.markdown("<h1 class='main-header'>🏭 MHE Equipment Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Real-time Monitoring & Predictive Maintenance for Material Handling Equipment</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    st.markdown("---")
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    st.write(f"Total Equipment: {len(data['equipment_master'])}")
    st.write(f"Total Failures: {len(data['failure_analysis'])}")
    st.write(f"Scheduled Maintenance: {len(data['maintenance_schedule'])}")
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filters")
    
    # Equipment Type Filter
    equipment_types = st.multiselect(
        "Equipment Types",
        options=data['equipment_master']['Equipment_Type'].unique(),
        default=data['equipment_master']['Equipment_Type'].unique()
    )
    
    # Status Filter
    status_filter = st.multiselect(
        "Status",
        options=data['equipment_master']['Status'].unique(),
        default=data['equipment_master']['Status'].unique()
    )
    
    # Criticality Filter
    criticality_filter = st.multiselect(
        "Criticality",
        options=data['equipment_master']['Criticality'].unique(),
        default=data['equipment_master']['Criticality'].unique()
    )
    
    # Location Filter
    location_filter = st.multiselect(
        "Locations",
        options=data['equipment_master']['Location'].unique(),
        default=data['equipment_master']['Location'].unique()
    )
    
    st.markdown("---")
    
    # Export Options
    st.subheader("📤 Export Options")
    
    if st.button("📊 Export Equipment CSV", use_container_width=True):
        csv = data['equipment_master'].to_csv(index=False)
        st.download_button(
            label="Download Equipment Data",
            data=csv,
            file_name="mhe_equipment_data.csv",
            mime="text/csv"
        )
    
    if st.button("⚠️ Export Failure Report", use_container_width=True):
        csv = data['failure_analysis'].to_csv(index=False)
        st.download_button(
            label="Download Failure Data",
            data=csv,
            file_name="mhe_failure_data.csv",
            mime="text/csv"
        )

# Apply Filters
filtered_equipment = data['equipment_master'].copy()
if equipment_types:
    filtered_equipment = filtered_equipment[filtered_equipment['Equipment_Type'].isin(equipment_types)]
if status_filter:
    filtered_equipment = filtered_equipment[filtered_equipment['Status'].isin(status_filter)]
if criticality_filter:
    filtered_equipment = filtered_equipment[filtered_equipment['Criticality'].isin(criticality_filter)]
if location_filter:
    filtered_equipment = filtered_equipment[filtered_equipment['Location'].isin(location_filter)]

# Main Dashboard Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview Dashboard",
    "🏗️ Equipment Management",
    "⚠️ Failure Analysis",
    "🔧 Maintenance Planning",
    "👨‍🔧 Operator Performance"
])

# ================== TAB 1: OVERVIEW DASHBOARD ==================
with tab1:
    # Key Performance Indicators
    st.subheader("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_equip = len(data['equipment_master'])
        st.metric(
            "Total Equipment",
            total_equip,
            delta=f"{len(data['equipment_master']['Equipment_Type'].unique())} Types"
        )
    
    with col2:
        operational_count = len(data['equipment_master'][data['equipment_master']['Status'] == 'Operational'])
        st.metric(
            "Operational",
            operational_count,
            delta=f"{(operational_count/total_equip)*100:.1f}% of Fleet"
        )
    
    with col3:
        total_row = data['summary_stats'][data['summary_stats']['Equipment_Type'] == 'TOTAL'].iloc[0]
        st.metric(
            "Avg Utilization",
            f"{total_row['Avg_Utilization_Pct']:.1f}%",
            delta="+2.3% vs Last Month"
        )
    
    with col4:
        st.metric(
            "Total Downtime",
            f"{total_row['Total_Downtime_Hours']:.0f} hrs",
            delta="-15 hrs vs Last Month"
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Utilization by Equipment Type")
        
        summary_no_total = data['summary_stats'][data['summary_stats']['Equipment_Type'] != 'TOTAL']
        
        fig = px.bar(
            summary_no_total,
            x='Equipment_Type',
            y='Avg_Utilization_Pct',
            color='Equipment_Type',
            color_discrete_sequence=px.colors.qualitative.Set2,
            text_auto=True
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="Utilization (%)",
            xaxis_title="Equipment Type"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⏱️ MTBF Comparison (Hours)")
        
        fig = px.bar(
            summary_no_total,
            x='Equipment_Type',
            y='Avg_MTBF_Hours',
            color='Avg_MTBF_Hours',
            color_continuous_scale='Greens',
            text_auto=True
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="MTBF (Hours)",
            xaxis_title="Equipment Type"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 MTTR by Equipment Type (Hours)")
        
        fig = px.bar(
            summary_no_total,
            x='Equipment_Type',
            y='Avg_MTTR_Hours',
            color='Avg_MTTR_Hours',
            color_continuous_scale='Reds',
            text_auto=True
        )
        fig.update_layout(
            showlegend=False,
            height=400,
            yaxis_title="MTTR (Hours)",
            xaxis_title="Equipment Type"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Maintenance Cost Distribution")
        
        fig = px.pie(
            summary_no_total,
            values='Total_Maintenance_Cost_YTD',
            names='Equipment_Type',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_layout(height=400)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Equipment Status Overview
    st.subheader("🏭 Equipment Status Overview")
    
    col1, col2, col3 = st.columns(3)
    
    status_counts = data['equipment_master']['Status'].value_counts()
    
    with col1:
        operational = status_counts.get('Operational', 0)
        st.markdown(f"""
        <div class="metric-card-green">
            <h3>✅ Operational</h3>
            <h1>{operational}</h1>
            <p>{total_equip} Total ({operational/total_equip*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        maintenance = status_counts.get('Under Maintenance', 0)
        st.markdown(f"""
        <div class="metric-card-orange">
            <h3>🔧 Under Maintenance</h3>
            <h1>{maintenance}</h1>
            <p>Total ({maintenance/total_equip*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        critical = len(data['equipment_master'][data['equipment_master']['Criticality'] == 'Critical'])
        st.markdown(f"""
        <div class="metric-card-red">
            <h3>🚨 Critical Equipment</h3>
            <h1>{critical}</h1>
            <p>Units Require Attention</p>
        </div>
        """, unsafe_allow_html=True)

# ================== TAB 2: EQUIPMENT MANAGEMENT ==================
with tab2:
    st.subheader("🏗️ Equipment Management")
    
    # Equipment Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_util = filtered_equipment['Utilization_Percentage'].mean()
        st.metric("Average Utilization", f"{avg_util:.1f}%")
    
    with col2:
        avg_mtbf = filtered_equipment['MTBF_Hours'].mean()
        st.metric("Average MTBF", f"{avg_mtbf:.1f} hrs")
    
    with col3:
        avg_mttr = filtered_equipment['MTTR_Hours'].mean()
        st.metric("Average MTTR", f"{avg_mttr:.1f} hrs")
    
    with col4:
        total_failures = filtered_equipment['Total_Failures'].sum()
        st.metric("Total Failures", total_failures)
    
    st.markdown("---")
    
    # Equipment Table
    st.subheader("📋 Equipment Details")
    
    # Add styling to dataframe display
    display_df = filtered_equipment.copy()
    display_df['Status_Badge'] = display_df['Status'].apply(
        lambda x: f"<span class='status-{x.lower().replace(' ', '')}'>{x}</span>"
    )
    
    st.dataframe(
        display_df,
        column_config={
            "Equipment_ID": st.column_config.TextColumn("Equipment ID", width="medium"),
            "Equipment_Type": st.column_config.TextColumn("Type", width="medium"),
            "Equipment_Name": st.column_config.TextColumn("Name", width="medium"),
            "Location": st.column_config.TextColumn("Location", width="medium"),
            "Utilization_Percentage": st.column_config.ProgressColumn(
                "Utilization",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "MTBF_Hours": st.column_config.NumberColumn("MTBF (hrs)", format="%.1f"),
            "MTTR_Hours": st.column_config.NumberColumn("MTTR (hrs)", format="%.1f"),
            "Total_Failures": st.column_config.NumberColumn("Failures", width="small"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
            "Criticality": st.column_config.TextColumn("Criticality", width="medium"),
            "Maintenance_Cost_YTD": st.column_config.NumberColumn("Cost YTD", format="$%d"),
            "Status_Badge": None
        },
        hide_index=True,
        use_container_width=True,
        height=500
    )
    
    st.markdown("---")
    
    # Equipment Details Cards
    st.subheader("🔍 Individual Equipment Analysis")
    
    # Select Equipment
    selected_equipment = st.selectbox(
        "Select Equipment to Analyze",
        options=filtered_equipment['Equipment_ID'].tolist(),
        format_func=lambda x: f"{x} - {filtered_equipment[filtered_equipment['Equipment_ID']==x]['Equipment_Name'].values[0]}"
    )
    
    if selected_equipment:
        equip_data = filtered_equipment[filtered_equipment['Equipment_ID'] == selected_equipment].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📍 Location</h4>
                <h3>{equip_data['Location']}</h3>
                <p>{equip_data['Department']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            status_color = "green" if equip_data['Status'] == 'Operational' else "orange"
            st.markdown(f"""
            <div class="metric-card-{'green' if equip_data['Status'] == 'Operational' else 'orange'}">
                <h4>📊 Status</h4>
                <h3>{equip_data['Status']}</h3>
                <p>Criticality: {equip_data['Criticality']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⏱️ MTBF / MTTR</h4>
                <h3>{equip_data['MTBF_Hours']:.1f} hrs</h3>
                <p>MTTR: {equip_data['MTTR_Hours']:.1f} hrs</p>
            </div>
            """, unsafe_allow_html=True)

# ================== TAB 3: FAILURE ANALYSIS ==================
with tab3:
    st.subheader("⚠️ Failure Analysis")
    
    # Failure Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_failures = len(data['failure_analysis'])
        st.metric("Total Failures", total_failures)
    
    with col2:
        critical_failures = len(data['failure_analysis'][data['failure_analysis']['Priority'] == 'Critical'])
        st.metric("Critical Failures", critical_failures)
    
    with col3:
        avg_downtime = data['failure_analysis']['Downtime_Hours'].mean()
        st.metric("Avg Downtime", f"{avg_downtime:.1f} hrs")
    
    with col4:
        total_repair_cost = data['failure_analysis']['Repair_Cost'].sum()
        st.metric("Total Repair Cost", f"${total_repair_cost:,}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Failure Types Distribution")
        
        failure_types = data['failure_analysis']['Failure_Type'].value_counts().head(10)
        
        fig = px.bar(
            x=failure_types.values,
            y=failure_types.index,
            orientation='h',
            color=failure_types.values,
            color_continuous_scale='Reds'
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Count",
            yaxis_title="Failure Type"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Root Cause Analysis")
        
        root_causes = data['failure_analysis']['Root_Cause'].value_counts().head(10)
        
        fig = px.bar(
            x=root_causes.values,
            y=root_causes.index,
            orientation='h',
            color=root_causes.values,
            color_continuous_scale='Oranges'
        )
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Count",
            yaxis_title="Root Cause"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Priority Distribution
    st.subheader("⚡ Priority Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        priority_counts = data['failure_analysis']['Priority'].value_counts()
        
        fig = px.pie(
            names=priority_counts.index,
            values=priority_counts.values,
            hole=0.5,
            color=priority_counts.index,
            color_discrete_map={
                'Critical': '#EF4444',
                'High': '#F59E0B',
                'Medium': '#3B82F6',
                'Low': '#10B981'
            }
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📅 Failures Over Time")
        
        failures_by_month = data['failure_analysis'].groupby(
            data['failure_analysis']['Failure_Date'].dt.to_period('M')
        ).size()
        
        fig = px.line(
            x=failures_by_month.index.astype(str),
            y=failures_by_month.values,
            markers=True
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent Failures Table
    st.subheader("📋 Recent Failures")
    
    failure_display = data['failure_analysis'].copy()
    failure_display['Failure_Date'] = failure_display['Failure_Date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        failure_display,
        column_config={
            "Failure_ID": st.column_config.TextColumn("Failure ID"),
            "Equipment_ID": st.column_config.TextColumn("Equipment"),
            "Failure_Type": st.column_config.TextColumn("Failure Type"),
            "Root_Cause": st.column_config.TextColumn("Root Cause"),
            "Downtime_Hours": st.column_config.NumberColumn("Downtime (hrs)", format="%.1f"),
            "Repair_Cost": st.column_config.NumberColumn("Cost", format="$%d"),
            "Priority": st.column_config.TextColumn("Priority")
        },
        hide_index=True,
        use_container_width=True,
        height=300
    )

# ================== TAB 4: MAINTENANCE PLANNING ==================
with tab4:
    st.subheader("🔧 Maintenance Planning")
    
    # Maintenance Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_maintenance = len(data['maintenance_schedule'])
        st.metric("Scheduled Maintenance", total_maintenance)
    
    with col2:
        preventive = len(data['maintenance_schedule'][data['maintenance_schedule']['Maintenance_Type'] == 'Preventive'])
        st.metric("Preventive", preventive)
    
    with col3:
        corrective = len(data['maintenance_schedule'][data['maintenance_schedule']['Maintenance_Type'] == 'Corrective'])
        st.metric("Corrective", corrective)
    
    with col4:
        total_cost = data['maintenance_schedule']['Estimated_Cost'].sum()
        st.metric("Total Cost", f"${total_cost:,}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Maintenance Type Distribution")
        
        maint_types = data['maintenance_schedule']['Maintenance_Type'].value_counts()
        
        fig = px.pie(
            names=maint_types.index,
            values=maint_types.values,
            hole=0.5,
            color=maint_types.index,
            color_discrete_map={
                'Preventive': '#10B981',
                'Corrective': '#EF4444'
            }
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚡ Priority Distribution")
        
        priority_counts = data['maintenance_schedule']['Priority'].value_counts()
        
        fig = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            color=priority_counts.index,
            color_discrete_map={
                'Critical': '#EF4444',
                'High': '#F59E0B',
                'Medium': '#3B82F6',
                'Low': '#10B981'
            }
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Maintenance Schedule Table
    st.subheader("📅 Maintenance Schedule")
    
    maint_display = data['maintenance_schedule'].copy()
    maint_display['Scheduled_Date'] = maint_display['Scheduled_Date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        maint_display,
        column_config={
            "Equipment_ID": st.column_config.TextColumn("Equipment"),
            "Equipment_Type": st.column_config.TextColumn("Type"),
            "Maintenance_Type": st.column_config.TextColumn("Type"),
            "Scheduled_Date": st.column_config.DateColumn("Date"),
            "Estimated_Duration_Hours": st.column_config.NumberColumn("Duration (hrs)", format="%d"),
            "Estimated_Cost": st.column_config.NumberColumn("Est. Cost", format="$%d"),
            "Priority": st.column_config.TextColumn("Priority"),
            "Assigned_Technician": st.column_config.TextColumn("Technician")
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )
    
    # Spare Parts Inventory
    st.subheader("📦 Spare Parts Inventory")
    
    # Identify low stock items
    spare_parts = data['spare_parts'].copy()
    spare_parts['Status'] = spare_parts.apply(
        lambda x: '🔴 Low Stock' if x['Current_Stock'] <= x['Reorder_Point'] else '🟢 In Stock',
        axis=1
    )
    
    low_stock_items = spare_parts[spare_parts['Current_Stock'] <= spare_parts['Reorder_Point']]
    
    if len(low_stock_items) > 0:
        st.warning(f"⚠️ **{len(low_stock_items)} items are below reorder point!**")
    
    st.dataframe(
        spare_parts,
        column_config={
            "Part_ID": st.column_config.TextColumn("Part ID"),
            "Part_Name": st.column_config.TextColumn("Part Name"),
            "Current_Stock": st.column_config.NumberColumn("Stock"),
            "Reorder_Point": st.column_config.NumberColumn("Reorder At"),
            "Unit_Cost": st.column_config.NumberColumn("Unit Cost", format="$%.2f"),
            "Lead_Time_Days": st.column_config.NumberColumn("Lead Time"),
            "Supplier": st.column_config.TextColumn("Supplier"),
            "Status": st.column_config.TextColumn("Status")
        },
        hide_index=True,
        use_container_width=True,
        height=300
    )

# ================== TAB 5: OPERATOR PERFORMANCE ==================
with tab5:
    st.subheader("👨‍🔧 Operator Performance")
    
    # Operator Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_operators = len(data['operator_performance'])
        st.metric("Total Operators", total_operators)
    
    with col2:
        avg_safety = data['operator_performance']['Safety_Score'].mean()
        st.metric("Avg Safety Score", f"{avg_safety:.1f}")
    
    with col3:
        total_incidents = data['operator_performance']['Incidents_Count'].sum()
        st.metric("Total Incidents", total_incidents)
    
    with col4:
        avg_training = data['operator_performance']['Training_Hours_YTD'].mean()
        st.metric("Avg Training Hours", f"{avg_training:.0f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Safety Score Distribution")
        
        fig = px.histogram(
            data['operator_performance'],
            x='Safety_Score',
            nbins=10,
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(
            height=350,
            showlegend=False,
            xaxis_title="Safety Score",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📚 Training Hours by Operator")
        
        top_operators = data['operator_performance'].nlargest(10, 'Training_Hours_YTD')
        
        fig = px.bar(
            top_operators,
            x='Operator_Name',
            y='Training_Hours_YTD',
            color='Safety_Score',
            color_continuous_scale='Greens'
        )
        fig.update_layout(
            height=350,
            xaxis_title="Operator",
            yaxis_title="Training Hours"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Department Performance
    st.subheader("🏭 Performance by Department")
    
    dept_stats = data['operator_performance'].groupby('Department').agg({
        'Safety_Score': 'mean',
        'Incidents_Count': 'sum',
        'Training_Hours_YTD': 'sum',
        'Operator_ID': 'count'
    }).round(2)
    dept_stats.columns = ['Avg Safety', 'Incidents', 'Training Hours', 'Operators']
    
    st.dataframe(
        dept_stats,
        column_config={
            "Avg Safety": st.column_config.NumberColumn("Avg Safety", format="%.1f"),
            "Incidents": st.column_config.NumberColumn("Incidents"),
            "Training Hours": st.column_config.NumberColumn("Training Hours"),
            "Operators": st.column_config.NumberColumn("Operators")
        },
        use_container_width=True
    )
    
    # Operator Table
    st.subheader("👥 Operator Details")
    
    st.dataframe(
        data['operator_performance'],
        column_config={
            "Operator_ID": st.column_config.TextColumn("ID"),
            "Operator_Name": st.column_config.TextColumn("Name"),
            "Department": st.column_config.TextColumn("Department"),
            "Total_Operating_Hours": st.column_config.NumberColumn("Operating Hours"),
            "Incidents_Count": st.column_config.NumberColumn("Incidents"),
            "Safety_Score": st.column_config.ProgressColumn(
                "Safety Score",
                format="%.0f",
                min_value=0,
                max_value=100
            ),
            "Training_Hours_YTD": st.column_config.NumberColumn("Training Hours")
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; padding: 1rem;">
    <p>📊 <strong>MHE Equipment Analytics Dashboard</strong></p>
    <p>For support, contact: maintenance@company.com | Version 1.0.0</p>
</div>
""", unsafe_allow_html=True)
