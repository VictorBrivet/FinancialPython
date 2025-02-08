# Financial Python

## Finance and appV2
This project is an interactive stock market analysis dashboard built with Python, Dash, and Plotly. It allows users to dynamically select stocks, define a custom date range, and analyze key financial metrics, including volatility, beta, Sharpe ratio, and correlation matrix. The dashboard is designed to be fully scalable and adaptable for financial data analysis in banking and investment contexts.
 
### Features
Dynamic Stock Selection – Users input tickers directly in Dash.
Custom Date Range – Adjustable analysis period.
Automated Data Fetching – Market data retrieved dynamically.
Key Financial Metrics:
Price Evolution (with and without index)
Cumulative Returns
Volatility (Annualized)
Beta vs. Index
Sharpe Ratio
Correlation Matrix

### Technology Stack
Python – Core language for data processing
Dash & Plotly – Interactive visualizations
Yahoo Finance API – Real-time market data retrieval
Pandas & NumPy – Financial computations and data structuring

### Usage
Enter stock tickers (e.g., LVMH, BNP.PA, AIR.PA)
Select the desired time range
Click the update button to fetch and visualize data
Analyze financial performance across multiple metrics

## Monte-Carlo
This project implements a Monte Carlo simulation for stock price forecasting using Python, NumPy, Pandas, and Matplotlib. It allows users to select a stock, define a custom historical period, and generate future price trajectories based on historical returns and volatility. The model is designed for financial risk assessment and investment analysis, providing insights into potential price ranges and market trends.

### Features
Dynamic Stock Selection – Users enter a stock ticker for analysis.
Custom Date Range – Historical period is fully adjustable.
Monte Carlo Simulation – Thousands of price trajectories are generated based on historical volatility.
Confidence Intervals – 5%-95% price range estimation.
Real Market Data Comparison – Forecasts are compared with actual stock prices.
Performance Metrics – Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) assess model reliability.

### Technology Stack
Python – Core language for simulation and analysis.
NumPy & Pandas – Data manipulation and financial computations.
Matplotlib & Seaborn – Visualization of stock trends and predictions.
Yahoo Finance API – Real-time market data retrieval.

### Usage
Enter a stock ticker (e.g., MC.PA for LVMH).
Set a historical period for data retrieval.
Define the forecast horizon (e.g., 1 to 5 years).
Run Monte Carlo simulation to visualize future price scenarios.
Compare simulated prices with real market data for reliability assessment
