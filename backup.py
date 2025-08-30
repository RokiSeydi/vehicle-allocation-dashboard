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

from core.style import get_custom_css

st.markdown(get_custom_css(), unsafe_allow_html=True)



from core.data import process_time_data, check_vehicle_conflicts
from core.charts import create_gantt_chart, create_utilization_chart, create_daily_allocation_chart
from core.sidebar import display_sidebar

def main():
    st.markdown('<h1 class="main-header">🚛 Vehicle Allocation Dashboard</h1>', unsafe_allow_html=True)

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload an Excel file to see the dashboard in action."
    )

    df_raw = None
    if uploaded_file:
        try:
            df_raw = pd.read_excel(uploaded_file, header=0)
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

    # Display sidebar and get state
    state = display_sidebar(df_raw, uploaded_file)

    if state['mapping_status'] == "complete":
        processed_df = process_time_data(state['df'])

        # Apply filters from sidebar state
        filtered_df = processed_df.copy()
        if state['search_term']:
            filtered_df = filtered_df[filtered_df['Vehicle_ID'].str.contains(state['search_term'], case=False, na=False)]
        if state['selected_vehicles']:
            filtered_df = filtered_df[filtered_df['Vehicle_ID'].isin(state['selected_vehicles'])]
        if state['selected_route'] != 'All':
            filtered_df = filtered_df[filtered_df['Route'] == state['selected_route']]
        if state['selected_day'] != 'All':
            filtered_df = filtered_df[filtered_df['Day'] == state['selected_day']]

        # Display main content
        display_main_content(filtered_df)
        
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
                <div style=\"background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;\">
                    <h5 style=\"margin: 0; color: white; font-size: 0.9rem;\">🕐 Peak Start Time</h5>
                    <p style=\"margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;\">{peak_hour:02d}:00</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                busiest_vehicle = filtered_df['Vehicle_ID'].value_counts().index[0]
                allocations = filtered_df['Vehicle_ID'].value_counts().iloc[0]
                st.markdown(f"""
                <div style=\"background: linear-gradient(135deg, #10b981, #059669); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;\">
                    <h5 style=\"margin: 0; color: white; font-size: 0.9rem;\">🚛 Busiest Vehicle</h5>
                    <p style=\"margin: 0.25rem 0 0 0; font-size: 0.95rem; font-weight: bold; color: white;\">{busiest_vehicle}</p>
                    <p style=\"margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.9);\">({allocations} trips)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                longest_trip = filtered_df['Duration'].max()
                st.markdown(f"""
                <div style=\"background: linear-gradient(135deg, #f59e0b, #d97706); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;\">
                    <h5 style=\"margin: 0; color: white; font-size: 0.9rem;\">⏱️ Longest Trip</h5>
                    <p style=\"margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;\">{longest_trip:.1f}h</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                if selected_day == 'All':
                    busiest_day = filtered_df['Day'].value_counts().index[0]
                    day_count = filtered_df['Day'].value_counts().iloc[0]
                    st.markdown(f"""
                    <div style=\"background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;\">
                        <h5 style=\"margin: 0; color: white; font-size: 0.9rem;\">📅 Busiest Day</h5>
                        <p style=\"margin: 0.25rem 0 0 0; font-size: 0.95rem; font-weight: bold; color: white;\">{busiest_day}</p>
                        <p style=\"margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.9);\">({day_count} trips)</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    day_total = len(filtered_df)
                    st.markdown(f"""
                    <div style=\"background: linear-gradient(135deg, #8b5cf6, #7c3aed); padding: 0.5rem; border-radius: 0.375rem; color: white; text-align: center;\">
                        <h5 style=\"margin: 0; color: white; font-size: 0.9rem;\">📅 {selected_day}</h5>
                        <p style=\"margin: 0.25rem 0 0 0; font-size: 1.2rem; font-weight: bold; color: white;\">{day_total} trips</p>
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
