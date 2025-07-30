# 🚛 Vehicle Allocation Dashboard

A powerful, interactive Streamlit dashboard for visualizing and analyzing vehicle allocation data. Perfect for fleet management, transportation planning, and resource optimization.

## ✨ Features

### 📊 Interactive Visualizations
- **Gantt Timeline Chart**: Weekly view of vehicle schedules with timeline at the top
- **Vehicle Utilization Analysis**: Bar chart showing total hours per vehicle
- **Daily Allocation Overview**: Breakdown by day of the week
- **Quick Insights Cards**: Compact gradient cards showing key metrics

### 🎨 Smart Design
- **Vehicle-Based Color Coding**: Consistent colors across all charts for easy vehicle tracking
- **Responsive Layout**: Works on desktop and mobile devices
- **Professional Styling**: Modern gradient design with clean typography

### 📁 Flexible Data Import
- **Excel File Support**: Upload .xlsx and .xls files
- **Intelligent Column Mapping**: Auto-detects common column patterns
- **Flexible Header Detection**: Handle files with headers in different rows
- **Smart Suggestions**: Automatic mapping recommendations

### 🔍 Advanced Features
- **Conflict Detection**: Automatically identifies scheduling overlaps
- **Interactive Filtering**: Filter by journey type/category and day of week
- **Hover Details**: Rich tooltip information on all charts
- **Data Validation**: Robust error handling and data cleaning

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/vehicle-allocation-dashboard.git
   cd vehicle-allocation-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser**
   - The dashboard will automatically open at `http://localhost:8501`
   - Upload your Excel file and start analyzing!

## 📋 Data Format

Your Excel file should contain the following columns (names can vary):

### Required Columns
- **Day**: Day of the week (e.g., "Monday", "Tuesday")
- **Vehicle ID**: Vehicle identifier (e.g., "Van 001", "Car 002")
- **Departure Time**: Start time (e.g., "08:00", "09:30")
- **Arrival Time**: End time (e.g., "15:30", "17:00")

### Optional Columns
- **Journey Purpose/Type**: Category of journey
- **Route/Destination**: Location information
- **Passengers**: Number of passengers

### Example Data Structure
```
Day       | Vehicle ID | Departure Time | Arrival Time | Journey Purpose
Monday    | Van 001    | 08:00         | 15:30        | School Run
Tuesday   | Car 002    | 09:30         | 11:00        | Hospital Visit
Wednesday | Van 001    | 10:15         | 12:30        | Shopping Trip
```

## 🎯 Use Cases

- **Fleet Management**: Optimize vehicle utilization and identify inefficiencies
- **Transportation Planning**: Visualize daily and weekly allocation patterns
- **Conflict Resolution**: Automatically detect and resolve scheduling conflicts
- **Resource Optimization**: Balance workload across vehicles
- **Reporting**: Generate insights for stakeholders and management

## 🛠️ Built With

- **[Streamlit](https://streamlit.io/)**: Web application framework
- **[Plotly](https://plotly.com/python/)**: Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)**: Data manipulation and analysis
- **[OpenPyXL](https://openpyxl.readthedocs.io/)**: Excel file processing
- Interactive hover information
- Filterable by various criteria

### Analytics Charts
- **Vehicle Utilization**: Total hours per vehicle
- **Daily Allocation**: Number of vehicles per day by size

### Metrics Panel
- Total vehicles count
- Total allocations
- Average duration
- Total operational hours

## Sample Data

The application includes sample data for demonstration. You can download the Excel template from the sidebar to see the expected data format.