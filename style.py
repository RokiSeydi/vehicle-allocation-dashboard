def get_custom_css():
    return """
        /* --- General & Headers --- */
        .main-header {
            font-size: 2.5rem; font-weight: bold; text-align: center; padding: 1rem;
            background: linear-gradient(90deg, #0047AB, #002355); /* Cobalt Blue Gradient */
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
        }
        .stExpander > div[role="button"] > div {
            font-weight: bold; color: #0047AB; /* Cobalt Blue */
        }

        /* --- Containers & Cards --- */
        .welcome-container {
            background-color: #f0f8ff; border-left: 5px solid #0047AB; /* Cobalt Blue */
            padding: 20px; border-radius: 5px; margin-bottom: 20px;
        }
        .metric-card {
            background: #f0fff0; /* Premium Green Light */
            padding: 1rem; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #2E8B57; /* Premium Green */
        }

        /* --- Passenger Capacity Manager Buttons --- */
        div[data-testid*="stButton"] > button {
            width: 40px !important; height: 40px !important;
            border: 2px solid #ccc !important;
            border-radius: 10px !important;
            background-color: #fff !important;
            color: #888 !important; font-size: 24px !important; font-weight: bold !important;
            line-height: 1 !important;
        }
        div[data-testid*="stButton"] > button:hover { border-color: #999 !important; color: #333 !important; }

        /* --- Progress Bar Styling --- */
        .stProgress > div > div > div > div { border-radius: 0.5rem; }
        .green-bar { background-color: #22c55e; }
        .orange-bar { background-color: #f97316; }
        .red-bar { background-color: #ef4444; }
    """
