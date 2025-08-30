# 🚛 Vehicle Allocation Dashboard

A powerful, interactive Streamlit dashboard for visualizing and analyzing vehicle allocation data. Perfect for fleet management, transportation planning, and resource optimization.

## ✨ Features

- **Interactive Gantt Timeline**: Visualize weekly vehicle schedules with an interactive timeline.
- **Vehicle Utilization Analysis**: Track total operational hours for each vehicle.
- **Daily Allocation Overview**: See a breakdown of journeys per day.
- **Conflict Detection**: Automatically identifies and flags scheduling overlaps.
- **Advanced Filtering**: Filter data by vehicle, route, and day.
- **Data Export**: Download filtered data to Excel or CSV.
- **Flexible Data Import**: Upload your own Excel files with custom column mapping.
- **Modern UI**: Clean, responsive, and professionally styled interface.

## 📂 Project Structure

The project has been refactored for simplicity and now follows a flat structure:

- `app.py`: The main Streamlit application file containing all logic.
- `style.py`: Contains all the CSS styling for the dashboard.
- `backup.py`: A backup of the previous, modular version of the app.
- `requirements.txt`: A list of all Python dependencies.
- `README.md`: This file.

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/vehicle-allocation-dashboard.git
    cd vehicle-allocation-dashboard
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the dashboard**
    ```bash
    streamlit run app.py
    ```

4.  **Open in browser**
    The dashboard will open at `http://localhost:8501`. Upload your Excel file to get started.

## 📋 Data Format

Your Excel file should contain columns for:

- **Day**: Day of the week (e.g., "Monday")
- **Vehicle ID**: A unique identifier for the vehicle (e.g., "Van 001")
- **Departure Time**: Journey start time (e.g., "08:00")
- **Arrival Time**: Journey end time (e.g., "15:30")

Optional columns like `Route`, `Vehicle Size`, and `Journey Purpose` are also supported. A template can be downloaded from the application's sidebar.

## 🛠️ Built With

- **[Streamlit](https://streamlit.io/)**: Web application framework
- **[Plotly](https://plotly.com/python/)**: Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)**: Data manipulation and analysis
- **[OpenPyXL](https://openpyxl.readthedocs.io/)**: For reading and writing Excel files.