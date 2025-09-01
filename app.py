import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

# --- Data Processing Functions ---
def process_time_data(df):
    df_processed = df.copy()
    day_mapping = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    processed_data = []
    for _, row in df_processed.iterrows():
        try:
            if pd.isna(row['Day']) or pd.isna(row['Departure_Time']) or pd.isna(row['Arrival_Time']):
                continue
            dep_time_str = str(row['Departure_Time']).strip()
            arr_time_str = str(row['Arrival_Time']).strip()
            if dep_time_str.lower() in ['nan', 'none', ''] or arr_time_str.lower() in ['nan', 'none', '']:
                continue
            try:
                dep_time = datetime.strptime(dep_time_str, '%H:%M').time()
                arr_time = datetime.strptime(arr_time_str, '%H:%M').time()
            except ValueError:
                try:
                    dep_time = datetime.strptime(dep_time_str, '%H:%M').time()
                    arr_time = datetime.strptime(arr_time_str, '%H:%M').time()
                except ValueError:
                    try:
                        if ' ' in dep_time_str:
                            dep_time = datetime.strptime(dep_time_str.split(' ')[1][:5], '%H:%M').time()
                        else:
                            dep_time = datetime.strptime(dep_time_str[:5], '%H:%M').time()
                        if ' ' in arr_time_str:
                            arr_time = datetime.strptime(arr_time_str.split(' ')[1][:5], '%H:%M').time()
                        else:
                            arr_time = datetime.strptime(arr_time_str[:5], '%H:%M').time()
                    except ValueError:
                        continue
            day_offset = day_mapping.get(row['Day'], 0)
            base_date = monday + timedelta(days=day_offset)
            departure_datetime = datetime.combine(base_date.date(), dep_time)
            arrival_datetime = datetime.combine(base_date.date(), arr_time)
            if arrival_datetime <= departure_datetime:
                arrival_datetime += timedelta(days=1)
            processed_data.append({
                'Vehicle_ID': row['Vehicle_ID'],
                'Vehicle_Size': row.get('Vehicle_Size', 'N/A'),
                'Day': row['Day'],
                'Route': row.get('Route', 'Unknown'),
                'Start': departure_datetime,
                'Finish': arrival_datetime,
                'Duration': (arrival_datetime - departure_datetime).total_seconds() / 3600
            })
        except Exception:
            continue
    return pd.DataFrame(processed_data)

def check_vehicle_conflicts(df):
    conflicts = []
    for vehicle_id in df['Vehicle_ID'].unique():
        vehicle_data = df[df['Vehicle_ID'] == vehicle_id].sort_values('Start')
        for i in range(len(vehicle_data) - 1):
            current = vehicle_data.iloc[i]
            next_allocation = vehicle_data.iloc[i + 1]
            if current['Finish'] > next_allocation['Start']:
                conflicts.append({
                    'Vehicle_ID': vehicle_id,
                    'Conflict_Time': f"{current['Finish'].strftime('%H:%M')} - {next_allocation['Start'].strftime('%H:%M')}",
                    'Day': current['Day'],
                    'Duration_Overlap': (current['Finish'] - next_allocation['Start']).total_seconds() / 3600
                })
    return pd.DataFrame(conflicts)

# --- Charting Functions ---
def create_gantt_chart(df):
    unique_vehicles = df['Vehicle_ID'].unique()
    vehicle_colors = ['#22c55e', '#f97316', '#dc2626', '#8b5cf6', '#06b6d4', '#84cc16', '#f59e0b', '#ef4444', '#3b82f6', '#ec4899', '#10b981', '#6366f1', '#14b8a6', '#f43f5e', '#a855f7', '#059669']
    vehicle_color_map = {vehicle: vehicle_colors[i % len(vehicle_colors)] for i, vehicle in enumerate(unique_vehicles)}
    df_sorted = df.sort_values(['Vehicle_ID', 'Start'])
    df_sorted['Vehicle_Day'] = df_sorted['Vehicle_ID'] + ' (' + df_sorted['Day'] + ')'
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Vehicle_ID", 
                        color="Vehicle_ID", title="Vehicle Allocation Gantt Chart",
                        hover_data=["Route", "Vehicle_Size"],
                        color_discrete_sequence=px.colors.qualitative.Vivid)

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="sans-serif",
        font_color="#333",
        title_font_color="#002355",
        legend_title_font_color="#002355"
    )
    fig.update_yaxes(categoryorder="total ascending")
    return fig

def create_utilization_chart(df):
    utilization = df.groupby('Vehicle_ID')['Duration'].sum().reset_index()
    fig = px.bar(utilization, x='Vehicle_ID', y='Duration', color='Vehicle_ID', 
                 title="Vehicle Utilization (Total Hours)",
                 color_discrete_sequence=px.colors.qualitative.Vivid)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family="sans-serif", font_color="#333",
        title_font_color="#002355", legend_title_font_color="#002355",
        xaxis_title="Vehicle", yaxis_title="Total Hours"
    )
    return fig

def create_daily_allocation_chart(df):
    daily_stats = df.groupby(['Day', 'Vehicle_ID']).size().reset_index(name='Count')
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats['Day'] = pd.Categorical(daily_stats['Day'], categories=day_order, ordered=True)
    daily_stats = daily_stats.sort_values('Day')
    fig = px.bar(daily_stats, x='Day', y='Count', color='Vehicle_ID', 
                 title="Daily Journey Allocation",
                 color_discrete_sequence=px.colors.qualitative.Vivid)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_family="sans-serif", font_color="#333",
        title_font_color="#002355", legend_title_font_color="#002355",
        xaxis_title="Day of Week", yaxis_title="Number of Journeys",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# --- Sidebar and Main Content Functions ---
def automatic_column_mapping(df_raw):
    COLUMN_MAPPING = {
        'Day': ['Day', 'day', 'Weekday'],
        'Vehicle_ID': ['Vehicle_ID', 'Vehicle', 'vehicle', 'Vehicle ID'],
        'Departure_Time': ['Departure_Time', 'Departure', 'Start Time', 'departure_time', 'Start'],
        'Arrival_Time': ['Arrival_Time', 'Arrival', 'End Time', 'arrival_time', 'Finish'],
        'Route': ['Route', 'route'],
        'Vehicle_Size': ['Vehicle_Size', 'Size', 'vehicle_size']
    }

    def find_column(df_columns, possible_names):
        for col in df_columns:
            cleaned_col = col.strip().lower()
            for name in possible_names:
                if name.lower() in cleaned_col:
                    return col
        return None

    mapped_cols = {}
    required_cols = ['Day', 'Vehicle_ID', 'Departure_Time', 'Arrival_Time']
    missing_cols = []

    for col_name in required_cols:
        found_col = find_column(df_raw.columns, COLUMN_MAPPING[col_name])
        if found_col:
            mapped_cols[col_name] = found_col
        else:
            missing_cols.append(col_name)
    
    if missing_cols:
        st.error(f"Upload failed. Missing required columns: {', '.join(missing_cols)}")
        return None

    df = pd.DataFrame()
    df['Day'] = df_raw[mapped_cols['Day']]
    df['Vehicle_ID'] = df_raw[mapped_cols['Vehicle_ID']]
    df['Departure_Time'] = df_raw[mapped_cols['Departure_Time']]
    df['Arrival_Time'] = df_raw[mapped_cols['Arrival_Time']]

    # Optional columns
    route_col = find_column(df_raw.columns, COLUMN_MAPPING['Route'])
    df['Route'] = df_raw[route_col] if route_col else 'Unknown'

    size_col = find_column(df_raw.columns, COLUMN_MAPPING['Vehicle_Size'])
    df['Vehicle_Size'] = df_raw[size_col] if size_col else 'N/A'

    return df

def display_sidebar(df):
    st.sidebar.header("📊 Dashboard Controls")
    state = {
        'selected_day': 'All', 
        'selected_vehicles': [], 
        'search_term': "", 
        'selected_route': 'All',
        'start_time': None,
        'end_time': None
    }

    st.sidebar.subheader("🔍 Filters")
    state['search_term'] = st.sidebar.text_input("Search Vehicle", "")
    
    vehicle_list = sorted(df['Vehicle_ID'].unique())
    state['selected_vehicles'] = st.sidebar.multiselect("Select Vehicles", options=vehicle_list)
    
    route_list = ['All'] + sorted(df['Route'].unique())
    state['selected_route'] = st.sidebar.selectbox("Filter by Route", options=route_list)
    
    days = ['All'] + list(df['Day'].unique())
    state['selected_day'] = st.sidebar.selectbox("Day of Week", days)

    st.sidebar.subheader("🕒 Time Range Filter")
    min_time = df['Start'].dt.time.min()
    max_time = df['Finish'].dt.time.max()

    state['start_time'] = st.sidebar.time_input("From Departure Time", value=min_time)
    state['end_time'] = st.sidebar.time_input("To Arrival Time", value=max_time)
    
    return state

def display_welcome_message():
    st.markdown("""
    <div class="welcome-container">
    <h2>🚛 Welcome to the Vehicle Allocation Dashboard</h2>
    <p>This powerful dashboard helps you visualize and analyze your vehicle allocation data.</p>
    
    <h3>🎯 What This Dashboard Does</h3>
    <ul>
        <li>✅ <strong>Interactive Gantt Charts</strong> - See vehicle schedules across the week</li>
        <li>✅ <strong>Conflict Detection</strong> - Automatically spot scheduling conflicts</li>
        <li>✅ <strong>Utilization Analysis</strong> - Track how efficiently vehicles are used</li>
        <li>✅ <strong>Day-by-Day Breakdown</strong> - Understand daily allocation patterns</li>
        <li>✅ <strong>Flexible Excel Import</strong> - Works with your existing Excel files</li>
    </ul>

    <h3>🚀 Getting Started</h3>
    <ol>
        <li><strong>Upload Your Excel File</strong> - Use the file uploader in the sidebar.</li>
        <li><strong>Automatic Column Mapping</strong> - The app will automatically detect your columns.</li>
        <li><strong>Explore Your Data</strong> - View interactive charts and insights.</li>
    </ol>
    
    <p>Your Excel file should contain columns for: Day/Date, Vehicle assignments, Departure and arrival times, and optionally Journey details.</p>

    <h3>🎨 Features Preview</h3>
    <p>📈 Timeline Charts | 🔍 Smart Filters | ⚠️ Conflict Alerts | 📊 Usage Statistics | 📱 Mobile Friendly</p>
    
    <h3>💡 Tips</h3>
    <ul>
        <li>Excel files with most common column names work automatically.</li>
        <li>Missing data is handled gracefully.</li>
        <li>All charts are interactive.</li>
        <li>You can export your filtered data.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def display_passenger_management(df):
    # Dynamic Passenger Manager (in sidebar, after filters)
    st.sidebar.subheader("🧑‍🤝‍🧑 Passenger Capacity Manager")

    # Unique vehicles from dataset
    vehicles = df['Vehicle_ID'].unique() if not df.empty else []

    # Initialize session state for counts
    if 'passenger_counts' not in st.session_state:
        st.session_state.passenger_counts = {v: 0 for v in vehicles}

    for vehicle in vehicles:
        if vehicle not in st.session_state.passenger_counts:
            st.session_state.passenger_counts[vehicle] = 0
        col1, col2, col3 = st.sidebar.columns([3,2,2])
        with col1:
            st.markdown(f"**{vehicle}**")
        with col2:
            if st.sidebar.button("−", key=f"minus_{vehicle}"):
                if st.session_state.passenger_counts[vehicle] > 0:
                    st.session_state.passenger_counts[vehicle] -= 1
                    st.rerun()
        with col3:
            if st.sidebar.button("+", key=f"plus_{vehicle}"):
                st.session_state.passenger_counts[vehicle] += 1
                st.rerun()
        # Show progress bar
        current = st.session_state.passenger_counts[vehicle]
        st.sidebar.progress(min(current/10, 1.0), text=f"{current} passengers")
        
def display_user_section():
():
    with st.sidebar.expander("👤 User Profile", expanded=False):
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        ">
            <div style="
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
            ">
                <div style="
                    width: 40px;
                    height: 40px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    backdrop-filter: blur(10px);
                    border: 2px solid rgba(255,255,255,0.3);
                ">
                    👤
                </div>
                <h4 style="margin: 0; font-size: 1.2rem; font-weight: bold;">Hello User</h4>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_quick_insights(df):
    """
    Show Quick Insights cards computed from the uploaded dataset.
    Does not modify global state or existing charts.
    """
    if df is None or df.empty:
        return

    st.subheader("⚡ Quick Insights")
    # Make sure we have the expected columns
    
        f"""
        <div style="margin-top:0.75rem;"></div>
        <div style="background: linear-gradient(135deg,#3b82f6,#1e40af); padding:16px; border-radius:12px; margin-bottom:12px; color:white;">
            <div style="font-weight:600; margin-bottom:4px;">🕒 Peak Start Time</div>
            <div style="font-size:24px; font-weight:800;">{(str(peak_hour).zfill(2) + ':00') if peak_hour is not None else '—'}</div>
        </div>
        <div style="background: linear-gradient(135deg,#10b981,#047857); padding:16px; border-radius:12px; margin-bottom:12px; color:white;">
            <div style="font-weight:600; margin-bottom:4px;">🚐 Busiest Vehicle</div>
            <div style="font-size:24px; font-weight:800;">{busiest_vehicle if busiest_vehicle else '—'}</div>
            <div style="opacity:0.9;">{f"({busiest_count} trips)" if busiest_count is not None else ""}</div>
        </div>
        <div style="background: linear-gradient(135deg,#f59e0b,#a16207); padding:16px; border-radius:12px; margin-bottom:12px; color:white;">
            <div style="font-weight:600; margin-bottom:4px;">⏱️ Longest Trip</div>
            <div style="font-size:24px; font-weight:800;">{(f"{longest_hours:.1f}h") if longest_hours is not None else "—"}</div>
        </div>
        <div style="background: linear-gradient(135deg,#8b5cf6,#5b21b6); padding:16px; border-radius:12px; margin-bottom:12px; color:white;">
            <div style="font-weight:600; margin-bottom:4px;">📅 Busiest Day</div>
            <div style="font-size:24px; font-weight:800;">{busiest_day if busiest_day else "—"}</div>
            <div style="opacity:0.9;">{f"({busiest_day_count} trips)" if busiest_day_count is not None else ""}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_main_content(df):
    display_passenger_management(df)
    
    if df.empty:
        st.info("No data available for the selected filters. Please adjust your filter settings.")
        return

    st.subheader("📈 Vehicle Allocation Timeline")
    gantt_fig = create_gantt_chart(df)
    st.plotly_chart(gantt_fig, use_container_width=True)
    # Quick Insights between Gantt chart and other charts
    display_quick_insights(df)


    conflicts_df = check_vehicle_conflicts(df)
    if not conflicts_df.empty:
        st.warning(f"⚠️ **{len(conflicts_df)} scheduling conflict(s) detected!**")
        with st.expander("View Conflicts Details"):
            st.dataframe(conflicts_df, use_container_width=True)
    else:
        st.success("✅ No scheduling conflicts detected!")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📊 Vehicle Utilization")
        utilization_fig = create_utilization_chart(df)
        st.plotly_chart(utilization_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("📅 Daily Breakdown")
        daily_fig = create_daily_allocation_chart(df)
        st.plotly_chart(daily_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    
    # --- Analytics Dashboard ---
    st.subheader("📊 Analytics Dashboard")
    if not df.empty:
        total_hours = df['Duration'].sum()
        # Core Fleet Utilisation Rate (as % of max 7*24h per vehicle)
        total_possible = len(df['Vehicle_ID'].unique()) * 7 * 24
        utilisation_rate = (total_hours/total_possible*100) if total_possible>0 else 0

        busiest_vehicle = df['Vehicle_ID'].value_counts().idxmax()
        busiest_count = df['Vehicle_ID'].value_counts().max()

        st.markdown(f"✅ **Core Fleet Utilisation Rate:** {utilisation_rate:.1f}%")
        st.markdown(f"📈 **Most Used Vehicle:** {busiest_vehicle} ({busiest_count} trips)")
        st.markdown("❌ **Sub-contractor Usage:** Data not available in current dataset")
        st.markdown("💰 **Cost Savings Potential:** Requires cost/ownership data")

    st.subheader("📋 Filtered Data")
    st.dataframe(df, use_container_width=True)

    # Export functionality
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='FilteredData')
    excel_data = output.getvalue()

    csv_data = df.to_csv(index=False).encode('utf-8')

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(label="📥 Download as Excel", data=excel_data, file_name='filtered_vehicle_data.xlsx')
    with col2:
        st.download_button(label="📥 Download as CSV", data=csv_data, file_name='filtered_vehicle_data.csv')

# --- Main Application ---
def get_custom_css():
    return """
        /* Quick Insights hover effect */
        .quick-card {
            transition: transform 0.2s ease-in-out;
        }
        .quick-card:hover {
            transform: scale(1.05);
        }

        h1[class="main-header"] {
            font-size: 2.5rem; font-weight: bold; text-align: center; padding: 1rem;
            background: linear-gradient(90deg, #0047AB, #002355);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .stExpander > div[role="button"] > div p {
            font-weight: bold; color: #0047AB;
        }
        .metric-card {
            background: #f0fff0; padding: 1rem; border-radius: 0.5rem; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 4px solid #2E8B57;
        }
        div[data-testid*="stButton"] > button {
            width: 35px !important; height: 35px !important; border: 1px solid #ccc !important;
            border-radius: 8px !important; background-color: #fff !important; color: #888 !important;
            font-size: 20px !important; font-weight: bold !important; line-height: 1 !important;
        }
    """

def main():
    st.set_page_config(page_title="Vehicle Allocation Dashboard", page_icon="🚛", layout="wide")
    st.markdown(f'<style>{get_custom_css()}</style>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🚛 Vehicle Allocation Dashboard</h1>', unsafe_allow_html=True)

    # Display user section in top left sidebar
    display_user_section()
    
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=['xlsx', 'xls'])

    if uploaded_file:
        df_raw = pd.read_excel(uploaded_file)
        mapped_df = automatic_column_mapping(df_raw)

        if mapped_df is not None:
            processed_df = process_time_data(mapped_df)
            state = display_sidebar(processed_df)

            filtered_df = processed_df.copy()
            if state['search_term']:
                filtered_df = filtered_df[filtered_df['Vehicle_ID'].str.contains(state['search_term'], case=False, na=False)]
            if state['selected_vehicles']:
                filtered_df = filtered_df[filtered_df['Vehicle_ID'].isin(state['selected_vehicles'])]
            if state['selected_route'] != 'All':
                filtered_df = filtered_df[filtered_df['Route'] == state['selected_route']]
            if state['selected_day'] != 'All':
                filtered_df = filtered_df[filtered_df['Day'] == state['selected_day']]

            if state['start_time']:
                filtered_df = filtered_df[filtered_df['Start'].dt.time >= state['start_time']]
            
            if state['end_time']:
                filtered_df = filtered_df[filtered_df['Finish'].dt.time <= state['end_time']]
            
            display_main_content(filtered_df)

            # Info section: How to Read the Gantt Chart
            with st.expander("ℹ️ How to Read the Gantt Chart", expanded=False):
                st.markdown("""
                **Understanding Your Vehicle Timeline:**

                🚛 **Y-Axis (Vertical):** Each row represents a different vehicle on a specific day  
                ⏰ **X-Axis (Horizontal):** Time of day from morning to evening  

                📊 **Colored Bars:** Each bar shows when a vehicle is allocated:  
                • Different colors represent different vehicles  
                • Each vehicle has its own unique color for easy identification  
                • Same vehicle = same color across all days  

                📏 **Bar Length:** Longer bars = longer journey duration  

                💡 **Interactive Features:**  
                • Hover over any bar for detailed information (vehicle, journey purpose, passengers, etc.)  
                • Click legend items to show/hide specific vehicles  
                • Drag to zoom in on specific time periods  
                • Use filters in sidebar to focus on specific data  
                """, unsafe_allow_html=True)
    else:
        display_welcome_message()

if __name__ == "__main__":
    main()