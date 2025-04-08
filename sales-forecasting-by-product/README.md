
# Sales Forecasting by Product Line

Forecasting monthly sales (bookings) by product line using both classical and machine learning models. The goal is to support strategic decision-making for sales planning, marketing campaigns, and resource allocation.

## Project Overview

This project models historical bookings across four product lines over a 3-year period to forecast the next 6 months of performance. We use:
- Facebook Prophet for time-series forecasting with seasonality and trend components
- XGBoost for comparison using machine learning on engineered time-based features

## Business Problem

Sales and finance leaders need forward-looking visibility into expected bookings by product line to:
- Guide quota and territory planning
- Align marketing and customer success efforts
- Adjust budget allocations based on product trends

## Folder Structure

project-root/
├── data/
│   └── sales_data.csv       # Raw sales data
├── notebooks/
│   └── sales_forecast_model.ipynb  # Jupyter Notebook for modeling
├── models/                  # Directory to store trained models
├── reports/
│   └── figures/             # Visualizations and plots
├── requirements.txt         # Project dependencies
└── README.md                # Project overview and documentation
