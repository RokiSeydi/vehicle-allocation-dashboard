# Vehicle Allocation Dashboard

A comprehensive Streamlit application for visualizing and managing vehicle allocation schedules using interactive Gantt charts and analytics.

## Features

- 📊 **Interactive Gantt Chart**: Visual timeline of vehicle allocations
- 📈 **Analytics Dashboard**: Vehicle utilization and daily allocation charts
- 📁 **Excel File Support**: Upload and process structured Excel data
- 🔍 **Dynamic Filtering**: Filter by vehicle size and day of week
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 📥 **Sample Template**: Download Excel template for data structure

## Required Excel Format

Your Excel file should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| Day | Day of the week | Monday, Tuesday, etc. |
| Vehicle_ID | Unique vehicle identifier | V001, V002, etc. |
| Vehicle_Size | Size category | Small, Medium, Large |
| Departure_Time | Start time (HH:MM format) | 08:00, 09:30, etc. |
| Arrival_Time | End time (HH:MM format) | 17:00, 16:30, etc. |
| Route | (Optional) Route information | Route A, Route B, etc. |

## Installation

1. Install required packages:
```bash
pip3 install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

1. **Upload Data**: Use the sidebar to upload your Excel file
2. **Apply Filters**: Filter by vehicle size or day of week
3. **View Analytics**: Explore the Gantt chart and utilization metrics
4. **Download Template**: Get a sample Excel template to structure your data

## Dashboard Components

### Main Gantt Chart
- Visual timeline showing vehicle allocations
- Color-coded by vehicle size
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