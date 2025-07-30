import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

# Page configuration
st.set_page_config(
    page_title="Vehicle Allocation Dashboard",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    
    .stSelectbox > div > div {
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)



def process_time_data(df):
    """Convert time strings to datetime objects for plotting"""
    df_processed = df.copy()
    
    # Create a mapping for days to dates (using current week)
    day_mapping = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }
    
    # Get current Monday as base date
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    
    processed_data = []
    
    for _, row in df_processed.iterrows():
        try:
            # Skip rows with missing critical data
            if pd.isna(row['Day']) or pd.isna(row['Departure_Time']) or pd.isna(row['Arrival_Time']):
                continue
                
            # Convert to string and clean up the time data
            dep_time_str = str(row['Departure_Time']).strip()
            arr_time_str = str(row['Arrival_Time']).strip()
            
            # Skip if time data is 'nan', 'None', or empty
            if dep_time_str.lower() in ['nan', 'none', ''] or arr_time_str.lower() in ['nan', 'none', '']:
                continue
            
            # Handle different time formats
            try:
                # Try to parse as HH:MM first
                dep_time = datetime.strptime(dep_time_str, '%H:%M').time()
                arr_time = datetime.strptime(arr_time_str, '%H:%M').time()
            except ValueError:
                try:
                    # Try to parse as H:MM (single digit hour)
                    dep_time = datetime.strptime(dep_time_str, '%H:%M').time()
                    arr_time = datetime.strptime(arr_time_str, '%H:%M').time()
                except ValueError:
                    try:
                        # Try parsing time from datetime string (e.g., "2024-01-01 14:30:00")
                        if ' ' in dep_time_str:
                            dep_time = datetime.strptime(dep_time_str.split(' ')[1][:5], '%H:%M').time()
                        else:
                            dep_time = datetime.strptime(dep_time_str[:5], '%H:%M').time()
                            
                        if ' ' in arr_time_str:
                            arr_time = datetime.strptime(arr_time_str.split(' ')[1][:5], '%H:%M').time()
                        else:
                            arr_time = datetime.strptime(arr_time_str[:5], '%H:%M').time()
                    except ValueError:
                        # If all parsing attempts fail, skip this row
                        print(f"Skipping row with unparseable time: {dep_time_str}, {arr_time_str}")
                        continue
            
            day_offset = day_mapping.get(row['Day'], 0)
            base_date = monday + timedelta(days=day_offset)
            
            # Combine date and time
            departure_datetime = datetime.combine(base_date.date(), dep_time)
            arrival_datetime = datetime.combine(base_date.date(), arr_time)
            
            # Handle cases where arrival is before departure (likely next day)
            if arrival_datetime <= departure_datetime:
                arrival_datetime += timedelta(days=1)
            
            processed_data.append({
                'Vehicle_ID': row['Vehicle_ID'],
                'Vehicle_Size': row['Vehicle_Size'],
                'Day': row['Day'],
                'Route': row.get('Route', 'Unknown'),
                'Start': departure_datetime,
                'Finish': arrival_datetime,
                'Duration': (arrival_datetime - departure_datetime).total_seconds() / 3600
            })
            
        except Exception as e:
            # Skip problematic rows and continue processing
            print(f"Skipping row due to error: {e}")
            continue
    
    return pd.DataFrame(processed_data)

def create_gantt_chart(df):
    """Create an enhanced interactive Gantt chart with better clarity showing days of the week"""
    # Enhanced color mapping for vehicles with better contrast
    unique_vehicles = df['Vehicle_ID'].unique()
    
    # Create a diverse color palette for vehicles
    vehicle_colors = [
        '#22c55e',  # Bright Green
        '#f97316',  # Orange  
        '#dc2626',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        '#84cc16',  # Lime
        '#f59e0b',  # Amber
        '#ef4444',  # Red-500
        '#3b82f6',  # Blue
        '#ec4899',  # Pink
        '#10b981',  # Emerald
        '#6366f1',  # Indigo
        '#14b8a6',  # Teal
        '#f43f5e',  # Rose
        '#a855f7',  # Violet
        '#059669'   # Green-600
    ]
    
    # Create color mapping for vehicles
    vehicle_color_map = {}
    for i, vehicle in enumerate(unique_vehicles):
        vehicle_color_map[vehicle] = vehicle_colors[i % len(vehicle_colors)]
    
    # Sort vehicles for better organization
    df_sorted = df.sort_values(['Vehicle_ID', 'Start'])
    
    # Create a combined Vehicle_Day identifier for better visualization
    df_sorted['Vehicle_Day'] = df_sorted['Vehicle_ID'] + ' (' + df_sorted['Day'] + ')'
    
    # Create the timeline chart - color by Vehicle_ID instead of Vehicle_Size
    fig = px.timeline(
        df_sorted, 
        x_start="Start", 
        x_end="Finish",
        y="Vehicle_Day",  # Changed from Vehicle_ID to show day info
        color="Vehicle_ID",  # Color by vehicle instead of journey type
        color_discrete_map=vehicle_color_map,
        hover_data=["Day", "Route", "Duration", "Vehicle_Size", "Journey_Purpose"] if 'Journey_Purpose' in df_sorted.columns else ["Day", "Route", "Duration", "Vehicle_Size"],
        title="🚛 Vehicle Allocation Timeline - Weekly View",
        labels={
            "Start": "Departure Time",
            "Finish": "Arrival Time", 
            "Vehicle_Day": "Vehicle (Day)",
            "Vehicle_ID": "Vehicle"
        }
    )
    
    # Enhanced layout with better spacing and grid
    fig.update_layout(
        height=max(500, len(df_sorted['Vehicle_Day'].unique()) * 40 + 250),  # Dynamic height
        xaxis_title="⏰ Timeline Across Week",
        yaxis_title="🚛 Vehicle (Day of Week)",
        title_font_size=22,
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Move legend further down from title
            xanchor="center",
            x=0.5,
            title="Vehicles",
            font=dict(size=12)
        ),
        plot_bgcolor='#f8fafc',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e2e8f0',
            tickformat='%a %H:%M',  # Show day abbreviation + time
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=11, color='#6b7280'),
            tickangle=45,
            side='top'  # Move timeline to top
        ),
        xaxis2=dict(
            showgrid=False,
            tickformat='%a %H:%M',
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=11, color='#6b7280'),
            tickangle=45,
            side='bottom',
            overlaying='x'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e2e8f0',
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=11, color='#6b7280'),
            categoryorder='category ascending'
        ),
        margin=dict(l=150, r=50, t=180, b=100)  # Increased top margin to accommodate title and legend
    )
    
    # Enhanced hover information and text display
    fig.update_traces(
        textposition="inside",
        texttemplate="<b>%{customdata[1]}</b><br>%{customdata[2]:.1f}h",
        textfont=dict(size=9, color='white'),
        hovertemplate="<b>🚛 Vehicle: %{legendgroup}</b><br>" +
                      "📅 Day: %{customdata[0]}<br>" +
                      "🛣️ Route: %{customdata[1]}<br>" +
                      "🕐 Departure: %{x|%a %H:%M}<br>" +
                      "🕐 Arrival: %{x_end|%a %H:%M}<br>" +
                      "⏱️ Duration: %{customdata[2]:.1f} hours<br>" +
                      "📏 Journey Type: %{customdata[3]}<br>" +
                      "<extra></extra>",
        marker=dict(
            line=dict(width=2, color='white')  # White border for better separation
        )
    )
    
    # Add time range annotations for better context
    fig.add_annotation(
        text="💡 Weekly View: Hover for details • Click legend to filter • Drag to zoom • Each row shows vehicle on specific day",
        xref="paper", yref="paper",
        x=0.5, y=-0.12,
        showarrow=False,
        font=dict(size=11, color='#6b7280'),
        xanchor="center"
    )
    
    return fig

def check_vehicle_conflicts(df):
    """Check for overlapping vehicle allocations"""
    conflicts = []
    
    for vehicle_id in df['Vehicle_ID'].unique():
        vehicle_data = df[df['Vehicle_ID'] == vehicle_id].sort_values('Start')
        
        for i in range(len(vehicle_data) - 1):
            current = vehicle_data.iloc[i]
            next_allocation = vehicle_data.iloc[i + 1]
            
            # Check if current allocation ends after next one starts
            if current['Finish'] > next_allocation['Start']:
                conflicts.append({
                    'Vehicle_ID': vehicle_id,
                    'Conflict_Time': f"{current['Finish'].strftime('%H:%M')} - {next_allocation['Start'].strftime('%H:%M')}",
                    'Day': current['Day'],
                    'Duration_Overlap': (current['Finish'] - next_allocation['Start']).total_seconds() / 3600
                })
    
    return pd.DataFrame(conflicts)

def create_utilization_chart(df):
    """Create vehicle utilization chart"""
    utilization = df.groupby(['Vehicle_ID', 'Vehicle_Size'])['Duration'].sum().reset_index()
    
    # Use the same vehicle color mapping as the Gantt chart
    unique_vehicles = df['Vehicle_ID'].unique()
    
    # Create a diverse color palette for vehicles (same as Gantt chart)
    vehicle_colors = [
        '#22c55e',  # Bright Green
        '#f97316',  # Orange  
        '#dc2626',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        '#84cc16',  # Lime
        '#f59e0b',  # Amber
        '#ef4444',  # Red-500
        '#3b82f6',  # Blue
        '#ec4899',  # Pink
        '#10b981',  # Emerald
        '#6366f1',  # Indigo
        '#14b8a6',  # Teal
        '#f43f5e',  # Rose
        '#a855f7',  # Violet
        '#059669'   # Green-600
    ]
    
    # Create color mapping for vehicles
    vehicle_color_map = {}
    for i, vehicle in enumerate(unique_vehicles):
        vehicle_color_map[vehicle] = vehicle_colors[i % len(vehicle_colors)]
    
    fig = px.bar(
        utilization,
        x='Vehicle_ID',
        y='Duration',
        color='Vehicle_ID',  # Color by vehicle instead of journey type
        title="Vehicle Utilization by Vehicle (Total Hours)",
        color_discrete_map=vehicle_color_map,
        labels={'Vehicle_ID': 'Vehicle'}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Vehicle ID",
        yaxis_title="Total Hours",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_daily_allocation_chart(df):
    """Create daily allocation overview with enhanced day-of-week analysis"""
    daily_stats = df.groupby(['Day', 'Vehicle_ID']).size().reset_index(name='Count')
    
    # Define day order for proper sorting
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats['Day'] = pd.Categorical(daily_stats['Day'], categories=day_order, ordered=True)
    daily_stats = daily_stats.sort_values('Day')
    
    # Use the same vehicle color mapping as the Gantt chart
    unique_vehicles = df['Vehicle_ID'].unique()
    
    # Create a diverse color palette for vehicles (same as Gantt chart)
    vehicle_colors = [
        '#22c55e',  # Bright Green
        '#f97316',  # Orange  
        '#dc2626',  # Red
        '#8b5cf6',  # Purple
        '#06b6d4',  # Cyan
        '#84cc16',  # Lime
        '#f59e0b',  # Amber
        '#ef4444',  # Red-500
        '#3b82f6',  # Blue
        '#ec4899',  # Pink
        '#10b981',  # Emerald
        '#6366f1',  # Indigo
        '#14b8a6',  # Teal
        '#f43f5e',  # Rose
        '#a855f7',  # Violet
        '#059669'   # Green-600
    ]
    
    # Create color mapping for vehicles
    vehicle_color_map = {}
    for i, vehicle in enumerate(unique_vehicles):
        vehicle_color_map[vehicle] = vehicle_colors[i % len(vehicle_colors)]
    
    fig = px.bar(
        daily_stats,
        x='Day',
        y='Count',
        color='Vehicle_ID',  # Color by vehicle instead of journey type
        title="📅 Daily Journey Allocation by Vehicle & Day of Week",
        color_discrete_map=vehicle_color_map,
        text='Count',
        labels={'Vehicle_ID': 'Vehicle'}
    )
    
    fig.update_layout(
        height=450,
        xaxis_title="📅 Day of Week",
        yaxis_title="Number of Vehicles",
        title_font_size=18,
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            tickangle=45,
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=12, color='#6b7280')
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#374151'),
            tickfont=dict(size=12, color='#6b7280')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.15,  # Move legend further down from title
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=60, r=50, t=120, b=80)  # Increased top margin to accommodate title and legend
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    
    return fig

# Main app
def main():
    st.markdown('<h1 class="main-header">🚛 Vehicle Allocation Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("📊 Dashboard Controls")
    
    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload any Excel file - you'll be able to map your columns to the required fields"
    )
    
    # Load data
    if uploaded_file is not None:
        try:
            # Try reading with different parameters to handle various Excel formats
            df_raw = pd.read_excel(uploaded_file, header=0)
            
            # Check if we have unnamed columns and try to fix them
            if any('Unnamed' in str(col) for col in df_raw.columns):
                st.sidebar.warning("⚠️ Detected unnamed columns. Trying alternative reading methods...")
                
                # Try reading without header first, then set header manually
                df_temp = pd.read_excel(uploaded_file, header=None)
                st.sidebar.info(f"📋 Raw file preview (first few rows):")
                
                # Show first few rows to help user identify the header row
                with st.sidebar.expander("🔍 Raw File Preview"):
                    st.dataframe(df_temp.head(5), use_container_width=True)
                
                # Let user select header row
                header_row = st.sidebar.selectbox(
                    "📍 Select Header Row (0-based index)",
                    options=list(range(min(10, len(df_temp)))),
                    index=2,  # Default to row 3 (index 2) as suggested
                    help="Select which row contains your column headers. Row 3 (index 2) is pre-selected as suggested."
                )
                
                # Re-read with selected header row
                df_raw = pd.read_excel(uploaded_file, header=header_row)
                
                # If still unnamed, let user manually name them
                if any('Unnamed' in str(col) for col in df_raw.columns):
                    st.sidebar.warning("📝 Still have unnamed columns. You can proceed with mapping, or try a different header row.")
                else:
                    st.sidebar.success(f"✅ Successfully used row {header_row + 1} as column headers!")
            
            st.sidebar.success("✅ File uploaded successfully!")
            
            # Show column mapping interface
            st.sidebar.subheader("🔗 Column Mapping")
            st.sidebar.info("Map your Excel columns to the dashboard fields:")
            
            # Clean column names and show them clearly
            available_columns = ['None'] + [f"{i}: {col}" if 'Unnamed' in str(col) else str(col) for i, col in enumerate(df_raw.columns)]
            
            # Show the actual columns detected
            with st.sidebar.expander("📋 Detected Columns"):
                for i, col in enumerate(df_raw.columns):
                    sample_val = str(df_raw[col].iloc[0]) if len(df_raw) > 0 else 'N/A'
                    st.write(f"**{i}: {col}**")
                    st.write(f"Sample: {sample_val}")
                    st.write("---")
            
            # Show detected columns that might match common patterns
            detected_suggestions = {}
            for i, col in enumerate(df_raw.columns):
                col_lower = str(col).lower()
                col_display = f"{i}: {col}" if 'Unnamed' in str(col) else str(col)
                
                if any(word in col_lower for word in ['day', 'date']):
                    detected_suggestions['day'] = col_display
                elif any(word in col_lower for word in ['vehicle', 'assigned', 'car', 'van', 'bus']):
                    detected_suggestions['vehicle'] = col_display
                elif any(word in col_lower for word in ['depart', 'departure', 'start', 'leave']):
                    detected_suggestions['departure'] = col_display
                elif any(word in col_lower for word in ['return', 'arrival', 'arrive', 'end', 'finish']):
                    detected_suggestions['arrival'] = col_display
                elif any(word in col_lower for word in ['passenger', 'people', 'pax', 'occupant']):
                    detected_suggestions['passengers'] = col_display
                elif any(word in col_lower for word in ['purpose', 'type', 'journey', 'trip', 'reason']):
                    detected_suggestions['purpose'] = col_display
                elif any(word in col_lower for word in ['route', 'destination', 'address', 'location', 'pickup', 'drop']):
                    detected_suggestions['route'] = col_display
            
            if detected_suggestions:
                st.sidebar.success(f"✨ Auto-detected {len(detected_suggestions)} potential matches!")
                with st.sidebar.expander("🎯 Suggested Mappings"):
                    for key, value in detected_suggestions.items():
                        st.write(f"**{key.title()}:** {value}")
            
            # Helper function to get column index from display name
            def get_column_name(display_name):
                if display_name == 'None':
                    return 'None'
                if ':' in display_name and display_name.split(':')[0].isdigit():
                    # Format: "0: ColumnName"
                    idx = int(display_name.split(':')[0])
                    return df_raw.columns[idx]
                else:
                    # Direct column name
                    return display_name
            
            # Column mapping with smart defaults
            day_col_display = st.sidebar.selectbox(
                "📅 Day Column", 
                available_columns, 
                index=available_columns.index(detected_suggestions.get('day', 'None')) if detected_suggestions.get('day') in available_columns else 0,
                key="day_mapping",
                help="Select the column containing day information (e.g., 'Day', 'Date')"
            )
            day_col = get_column_name(day_col_display)
            
            vehicle_col_display = st.sidebar.selectbox(
                "🚛 Vehicle/Assignment Column", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('vehicle', 'None')) if detected_suggestions.get('vehicle') in available_columns else 0,
                key="vehicle_mapping",
                help="Select the column with vehicle information (e.g., 'Assigned Vehicle Info')"
            )
            vehicle_col = get_column_name(vehicle_col_display)
            
            dept_col_display = st.sidebar.selectbox(
                "🕐 Departure Time Column", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('departure', 'None')) if detected_suggestions.get('departure') in available_columns else 0,
                key="dept_mapping",
                help="Select departure time column (e.g., 'Depart (time)')"
            )
            dept_col = get_column_name(dept_col_display)
            
            arr_col_display = st.sidebar.selectbox(
                "🕐 Arrival/Return Time Column", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('arrival', 'None')) if detected_suggestions.get('arrival') in available_columns else 0,
                key="arr_mapping",
                help="Select arrival time column (e.g., 'Return (Arrival Time)')"
            )
            arr_col = get_column_name(arr_col_display)
            
            # Optional columns
            st.sidebar.markdown("**Optional Columns:**")
            
            passengers_col = st.sidebar.selectbox(
                "� Passengers Column (Optional)", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('passengers', 'None')) if detected_suggestions.get('passengers') in available_columns else 0,
                key="passengers_mapping",
                help="Column showing number of passengers"
            )
            
            purpose_col_display = st.sidebar.selectbox(
                "🎯 Journey Purpose/Type (Optional)", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('purpose', 'None')) if detected_suggestions.get('purpose') in available_columns else 0,
                key="purpose_mapping",
                help="Journey purpose or type information"
            )
            purpose_col = get_column_name(purpose_col_display)
            
            route_col_display = st.sidebar.selectbox(
                "🛣️ Route/Destination (Optional)", 
                available_columns,
                index=available_columns.index(detected_suggestions.get('route', 'None')) if detected_suggestions.get('route') in available_columns else 0,
                key="route_mapping",
                help="Pick up address, destination, or route information"
            )
            route_col = get_column_name(route_col_display)
            
            # Check if required mappings are provided
            core_mappings = [day_col, vehicle_col, dept_col, arr_col]
            mapped_count = sum(1 for col in core_mappings if col != 'None')
            
            if all(col != 'None' for col in core_mappings):
                # Full mapping - all features available
                df = pd.DataFrame()
                df['Day'] = df_raw[day_col]
                df['Vehicle_ID'] = df_raw[vehicle_col]
                df['Departure_Time'] = df_raw[dept_col]
                df['Arrival_Time'] = df_raw[arr_col]
                
                # Handle optional columns
                if passengers_col != 'None':
                    df['Passengers'] = df_raw[passengers_col]
                else:
                    df['Passengers'] = 'Unknown'
                
                if purpose_col != 'None':
                    df['Journey_Purpose'] = df_raw[purpose_col]
                    # Use journey purpose as vehicle size category for color coding
                    df['Vehicle_Size'] = df_raw[purpose_col]
                else:
                    df['Journey_Purpose'] = 'Unknown'
                    df['Vehicle_Size'] = 'Standard'
                
                if route_col != 'None':
                    df['Route'] = df_raw[route_col]
                else:
                    df['Route'] = 'Unknown'
                
                # Convert time columns to string format if they aren't already
                df['Departure_Time'] = df['Departure_Time'].astype(str)
                df['Arrival_Time'] = df['Arrival_Time'].astype(str)
                
                # Clean time format (handle various time formats)
                df['Departure_Time'] = df['Departure_Time'].str.replace(r'^\d{4}-\d{2}-\d{2}\s+', '', regex=True)
                df['Arrival_Time'] = df['Arrival_Time'].str.replace(r'^\d{4}-\d{2}-\d{2}\s+', '', regex=True)
                
                st.sidebar.success("✅ Core mapping complete! All dashboard features available.")
                mapping_status = "complete"
                
                # Show preview of mapped data
                with st.sidebar.expander("👁️ Preview Mapped Data"):
                    st.dataframe(df.head(3), use_container_width=True)
                    
            elif mapped_count >= 2:
                # Partial mapping - limited features available
                st.sidebar.warning(f"⚠️ Partial mapping ({mapped_count}/4 core columns mapped)")
                st.sidebar.info("📊 You can still view your Excel data, but some charts may not be available.")
                mapping_status = "partial"
                # Create empty dataframe for partial mapping
                df = pd.DataFrame()
                
            else:
                # Minimal mapping - only Excel viewing available
                st.sidebar.warning("⚠️ Please map at least 2 columns for basic functionality")
                st.sidebar.info("📝 Currently only Excel data viewing is available.")
                mapping_status = "minimal"
                # Create empty dataframe for minimal mapping
                df = pd.DataFrame()
                
        except Exception as e:
            st.sidebar.error(f"❌ Error reading file: {str(e)}")
            mapping_status = "error"
    else:
        # No file uploaded
        st.sidebar.info("� Please upload an Excel file to begin.")
        mapping_status = "no_file"
    
    # Data validation - now more flexible
    if uploaded_file is not None and 'mapping_status' in locals():
        if mapping_status == "complete":
            # Full functionality available
            pass
        elif mapping_status == "partial":
            st.info("ℹ️ **Partial Mapping Active**: Some advanced features may be limited. Complete all column mappings for full functionality.")
        elif mapping_status == "minimal":
            st.warning("⚠️ **Limited Functionality**: Only Excel data viewing available. Map more columns to enable charts and analysis.")
        elif mapping_status == "error":
            st.error("❌ **Error Loading File**: Please check your Excel file format and try again.")
    elif uploaded_file is None:
        st.info("📤 **Welcome!** Upload an Excel file to get started with your vehicle allocation dashboard.")
        st.markdown("""
        ### Getting Started:
        1. 📁 **Upload Your Excel File** - Use the sidebar to upload your vehicle data
        2. 🔗 **Map Your Columns** - Tell us which columns contain what data
        3. 📊 **View Your Dashboard** - See interactive charts and analysis
        
        **Need a template?** Download the sample Excel template from the sidebar to see the expected format.
        """)
    
    # Only process data if we have a complete mapping and uploaded file
    if uploaded_file is not None and 'mapping_status' in locals() and mapping_status == "complete":
        # Process data
        processed_df = process_time_data(df)
        
        # Filters
        st.sidebar.subheader("🔍 Filters")
        
        # Journey type filter (formerly vehicle size)
        journey_types = ['All'] + list(df['Vehicle_Size'].unique())
        selected_type = st.sidebar.selectbox("Journey Type/Category", journey_types, help="Filter by journey purpose or type")
        
        # Day filter
        days = ['All'] + list(df['Day'].unique())
        selected_day = st.sidebar.selectbox("Day of Week", days)
        
        # Apply filters
        filtered_df = processed_df.copy()
        if selected_type != 'All':
            filtered_df = filtered_df[filtered_df['Vehicle_Size'] == selected_type]
        if selected_day != 'All':
            filtered_df = filtered_df[filtered_df['Day'] == selected_day]
    else:
        # No complete mapping available - limited functionality
        if uploaded_file is not None:
            # File uploaded but mapping incomplete
            processed_df = pd.DataFrame()
            filtered_df = pd.DataFrame()
            selected_type = "All"
            selected_day = "All"
            
            st.sidebar.subheader("⚠️ Charts Unavailable")
            st.sidebar.info("Complete column mapping to enable filters and charts.")
        else:
            # No file uploaded
            processed_df = pd.DataFrame()
            filtered_df = pd.DataFrame()
            selected_type = "All"
            selected_day = "All"
    
    # Main dashboard content - conditional based on mapping status
    if uploaded_file is not None and 'mapping_status' in locals() and mapping_status == "complete":
        # Full dashboard functionality
        st.header("🚐 Vehicle Allocation Dashboard")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Vehicles", len(filtered_df['Vehicle_ID'].unique()))
        
        with col2:
            st.metric("Total Allocations", len(filtered_df))
        
        with col3:
            avg_duration = filtered_df['Duration'].mean()
            st.metric("Avg Duration", f"{avg_duration:.1f}h")
        
        with col4:
            total_hours = filtered_df['Duration'].sum()
            st.metric("Total Hours", f"{total_hours:.1f}h")
    
        # Main charts
        st.subheader("📈 Vehicle Allocation Timeline")
        
        # Add explanation for the Gantt chart
        with st.expander("ℹ️ How to Read the Gantt Chart", expanded=False):
            st.markdown("""
            **Understanding Your Vehicle Timeline:**
            
            🚛 **Y-Axis (Vertical)**: Each row represents a different vehicle on a specific day
            
            ⏰ **X-Axis (Horizontal)**: Time of day from morning to evening
            
            📊 **Colored Bars**: Each bar shows when a vehicle is allocated:
            - Different colors represent different vehicles
            - Each vehicle has its own unique color for easy identification
            - Same vehicle = same color across all days
            
            📏 **Bar Length**: Longer bars = longer journey duration
            
            💡 **Interactive Features**:
            - Hover over any bar for detailed information (vehicle, journey purpose, passengers, etc.)
            - Click legend items to show/hide specific vehicles
            - Drag to zoom in on specific time periods
            - Use filters in sidebar to focus on specific data
            """)
        
        if not filtered_df.empty:
            gantt_fig = create_gantt_chart(filtered_df)
            st.plotly_chart(gantt_fig, use_container_width=True)
            
            # Add summary insights
            st.markdown("### 📊 Quick Insights")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                peak_hour = filtered_df.groupby(filtered_df['Start'].dt.hour).size().idxmax()
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;">
                    <h5 style="margin: 0; color: white; font-size: 0.9rem;">🕐 Peak Start Time</h5>
                    <p style="margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;">{peak_hour:02d}:00</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                busiest_vehicle = filtered_df['Vehicle_ID'].value_counts().index[0]
                allocations = filtered_df['Vehicle_ID'].value_counts().iloc[0]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #10b981, #059669); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;">
                    <h5 style="margin: 0; color: white; font-size: 0.9rem;">🚛 Busiest Vehicle</h5>
                    <p style="margin: 0.25rem 0 0 0; font-size: 0.95rem; font-weight: bold; color: white;">{busiest_vehicle}</p>
                    <p style="margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.9);">({allocations} trips)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                longest_trip = filtered_df['Duration'].max()
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f59e0b, #d97706); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;">
                    <h5 style="margin: 0; color: white; font-size: 0.9rem;">⏱️ Longest Trip</h5>
                    <p style="margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;">{longest_trip:.1f}h</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if selected_day == 'All':
                    busiest_day = filtered_df['Day'].value_counts().index[0]
                    day_count = filtered_df['Day'].value_counts().iloc[0]
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;">
                        <h5 style="margin: 0; color: white; font-size: 0.9rem;">📅 Busiest Day</h5>
                        <p style="margin: 0.25rem 0 0 0; font-size: 0.95rem; font-weight: bold; color: white;">{busiest_day}</p>
                        <p style="margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.9);">({day_count} trips)</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    day_total = len(filtered_df)
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;">
                        <h5 style="margin: 0; color: white; font-size: 0.9rem;">📅 {selected_day}</h5>
                        <p style="margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;">{day_total} trips</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            # Check for conflicts
            conflicts_df = check_vehicle_conflicts(filtered_df)
            if not conflicts_df.empty:
                st.warning(f"⚠️ **{len(conflicts_df)} scheduling conflict(s) detected!**")
                with st.expander("View Conflicts Details"):
                    st.dataframe(conflicts_df, use_container_width=True)
            else:
                st.success("✅ No scheduling conflicts detected!")
        else:
            st.warning("No data to display with current filters.")
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            if not filtered_df.empty:
                util_fig = create_utilization_chart(filtered_df)
                st.plotly_chart(util_fig, use_container_width=True)
        
        with col2:
            if not filtered_df.empty:
                daily_fig = create_daily_allocation_chart(filtered_df)
                st.plotly_chart(daily_fig, use_container_width=True)
                
    elif uploaded_file is not None and 'mapping_status' in locals() and mapping_status == "partial":
        # Limited dashboard functionality
        st.header("🚐 Vehicle Allocation Dashboard (Limited)")
        st.info("💡 **Tip**: Complete all column mappings in the sidebar to unlock full dashboard features!")
        
        # Show what we can with partial data
        if len(filtered_df) > 0:
            col1, col2 = st.columns(2)
            with col1:
                try:
                    st.metric("Total Records", len(filtered_df))
                except:
                    st.metric("Total Records", "N/A")
            with col2:
                try:
                    if 'Vehicle_ID' in filtered_df.columns:
                        st.metric("Unique Vehicles", len(filtered_df['Vehicle_ID'].unique()))
                    else:
                        st.metric("Unique Vehicles", "Map Vehicle ID column")
                except:
                    st.metric("Unique Vehicles", "N/A")
            
            st.subheader("📋 Available Data Preview")
            st.dataframe(filtered_df.head(10), use_container_width=True)
        else:
            st.warning("No data available to display.")
            
    elif uploaded_file is not None:
        # File uploaded but minimal mapping - just show Excel data viewing option
        st.header("📁 Excel File Viewer")
        st.info("📋 Your Excel file has been loaded successfully!")
        st.info("💡 **Next Step**: Complete column mapping in the sidebar to enable dashboard features.")
        
        # Show basic file info
        if 'df_raw' in locals() and df_raw is not None:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 Total Rows", len(df_raw))
            with col2:
                st.metric("📊 Total Columns", len(df_raw.columns))
            with col3:
                st.metric("📁 File Name", uploaded_file.name if uploaded_file else "N/A")
    
    else:
        # No file uploaded - show welcome/getting started page
        st.header("🚛 Welcome to Vehicle Allocation Dashboard")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### 🎯 What This Dashboard Does
            
            This powerful dashboard helps you visualize and analyze your vehicle allocation data:
            
            ✅ **Interactive Gantt Charts** - See vehicle schedules across the week  
            ✅ **Conflict Detection** - Automatically spot scheduling conflicts  
            ✅ **Utilization Analysis** - Track how efficiently vehicles are used  
            ✅ **Day-by-Day Breakdown** - Understand daily allocation patterns  
            ✅ **Flexible Excel Import** - Works with your existing Excel files  
            
            ### 🚀 Getting Started
            
            1. **📁 Upload Your Excel File** - Use the file uploader in the sidebar
            2. **🔗 Map Your Columns** - Tell us which columns contain what data  
            3. **📊 Explore Your Data** - View interactive charts and insights
            
            **Your Excel file should contain columns for:**
            - Day/Date information
            - Vehicle assignments  
            - Departure and arrival times
            - Journey details (optional)
            """)
        
        with col2:
            st.markdown("""
            ### 📋 Need a Template?
            
            Not sure about the format? 
            Upload any Excel file first, then download the template from the sidebar to see the expected structure.
            
            ### 🎨 Features Preview
            
            Once you upload your data, you'll see:
            
            📈 **Timeline Charts**  
            🔍 **Smart Filters**  
            ⚠️ **Conflict Alerts**  
            📊 **Usage Statistics**  
            📱 **Mobile Friendly**  
            
            ### 💡 Tips
            
            - Excel files with any column names work
            - Missing data is handled gracefully  
            - All charts are interactive
            - Export your visualizations
            """)
            
            # Add some visual elements
            st.markdown("---")
            st.info("🔒 **Privacy**: Your data stays on your computer. Nothing is stored or shared.")
            
    # Only show data table section if we have an uploaded file
    if uploaded_file is not None:
        # Data table
        st.subheader("📋 Raw Data")
        
        # Create tabs for different data views
        tab1, tab2 = st.tabs(["📊 Processed Data", "📄 Original Excel Data"])
        
        with tab1:
            if not filtered_df.empty and 'mapping_status' in locals() and mapping_status == "complete":
                st.markdown("**Processed data used for charts and analysis:**")
                st.dataframe(
                    filtered_df[['Vehicle_ID', 'Vehicle_Size', 'Day', 'Route', 'Start', 'Finish', 'Duration']],
                    use_container_width=True
                )
            else:
                st.info("📊 Complete column mapping to see processed data here.")
        
        with tab2:
            if 'df_raw' in locals():
                st.markdown("**Original Excel file data as uploaded:**")
                st.dataframe(df_raw, use_container_width=True)
                
                # Show file info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📄 Total Rows", len(df_raw))
                with col2:
                    st.metric("📊 Total Columns", len(df_raw.columns))
                with col3:
                    st.metric("📁 File Name", uploaded_file.name if uploaded_file else "N/A")
                    
                # Show column info
                with st.expander("📋 Column Information"):
                    col_info = pd.DataFrame({
                        'Column Name': df_raw.columns,
                        'Data Type': df_raw.dtypes.astype(str),
                        'Non-Null Count': df_raw.count(),
                        'Sample Value': [str(df_raw[col].iloc[0]) if len(df_raw) > 0 else 'N/A' for col in df_raw.columns]
                    })
                    st.dataframe(col_info, use_container_width=True)
            else:
                st.error("❌ No data available to display.")
        
        # Download sample template - only show when file is uploaded
        st.sidebar.subheader("📥 Download Template")
        
        # Create template based on expected structure
        template_data = {
            'Day': ['Monday', 'Tuesday', 'Wednesday'],
            'Journey Type': ['School Run', 'Hospital Visit', 'Shopping Trip'],
            'Depart (time)': ['08:00', '09:30', '10:15'],
            'Return (Arrival Time)': ['15:30', '11:00', '12:30'],
            'Passengers': ['4', '1', '2'],
            'Assigned Vehicle Info': ['Van 001', 'Car 002', 'Car 003'],
            'Journey Purpose': ['Education', 'Healthcare', 'Shopping'],
            'Journey Desc': ['School transport', 'Hospital appointment', 'Weekly shopping'],
            'Pick Up Address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
            'Destination': ['Green School', 'City Hospital', 'Shopping Centre']
        }
        template_df = pd.DataFrame(template_data)
        
        # Convert to Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            template_df.to_excel(writer, sheet_name='Vehicle_Data', index=False)
        
        st.sidebar.download_button(
            label="📄 Download Sample Excel Template",
            data=output.getvalue(),
            file_name="vehicle_allocation_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()