import pandas as pd
import yfinance as yf
import ta
import streamlit as st

# Define the stock screener function with debug statements
def calculate_indicators(data):
    # Check if the data is empty
    if data.empty:
        st.error("Data is empty")
        return data
    else:
        st.write("Data sample:", data.head())

    # Ensure 'Close' column exists
    if 'Close' not in data.columns:
        st.error("No 'Close' column found")
        return data

    try:
        # Extract the 'Close' column and ensure it's a Series
        close_series = data['Close'].squeeze()
        if not isinstance(close_series, pd.Series):
            st.error("'Close' column is not a pandas Series after squeezing")
            return data

        # Calculate EMA and RSI
        data['EMA_20'] = ta.trend.ema_indicator(close_series, window=20)
        data['EMA_50'] = ta.trend.ema_indicator(close_series, window=50)
        data['RSI'] = ta.momentum.rsi(close_series, window=14)

    except Exception as e:
        st.error(f"Error in calculating indicators: {e}")

    return data

# Function to screen stocks
def screen_stocks(symbols):
    results = []
    for symbol in symbols:
        try:
            st.write(f"Fetching data for {symbol}...")
            data = yf.download(symbol, period='6mo', interval='1d')

            if data.empty:
                st.warning(f"No data downloaded for {symbol}")
                continue  # Skip to the next symbol
            else:
                data = calculate_indicators(data)

            # Determine the uptrend condition
            if not data.empty and 'EMA_20' in data.columns and 'EMA_50' in data.columns and 'RSI' in data.columns:
                if len(data) >= 2:  # Ensure we have at least two data points
                    latest_ema20 = data['EMA_20'].iloc[-1]
                    latest_ema50 = data['EMA_50'].iloc[-1]
                    latest_rsi = data['RSI'].iloc[-1]
                    prev_ema20 = data['EMA_20'].iloc[-2]
                    prev_ema50 = data['EMA_50'].iloc[-2]

                    # Check for missing values before checking the condition
                    if not pd.isna(latest_ema20) and not pd.isna(latest_ema50) and not pd.isna(latest_rsi) and not pd.isna(prev_ema20) and not pd.isna(prev_ema50):
                        # Check for uptrend and RSI confirmation
                        is_uptrend = (latest_ema20 > latest_ema50) and (prev_ema20 <= prev_ema50)
                        is_rsi_above_50 = latest_rsi > 50

                        if is_uptrend and is_rsi_above_50:
                            st.success(f"{symbol} is in an uptrend")
                            results.append(symbol)
                        else:
                            st.write(f"{symbol} is not in an uptrend")
                    else:
                        st.warning(f"Insufficient data for {symbol}")
                else:
                    st.warning(f"Insufficient data points to determine trend for {symbol}")

        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")
    return results

# Streamlit App
st.title("Nifty 500 Stock Screener")

# Load the list of Nifty 500 symbols from the CSV file
try:
    nifty500_df = pd.read_csv("nifty500_stocks.csv")
    nifty500_symbols = nifty500_df["Symbol"].tolist()  # Assuming the symbol column is named "Symbol"
    st.write(f"Scanning {len(nifty500_symbols)} Nifty 500 stocks.")
except FileNotFoundError:
    st.error("Error: nifty500_stocks.csv not found. Please download the Nifty 500 stock list and save it as nifty500_stocks.csv in the same directory.")
    nifty500_symbols = []  # Initialize as empty if the file is not found
except KeyError as e:
    st.error(f"Error: Column '{e}' not found in nifty500_stocks.csv. Please ensure the CSV file has a column named 'Symbol' or update the code accordingly.")
    nifty500_symbols = []

# Initialize results in the global scope
results = []

if st.button("Run Screener"):
    if nifty500_symbols:
        st.write("Screening stocks...")
        results = screen_stocks(nifty500_symbols)
        st.write("Stocks in Uptrend:", results)
    else:
        st.warning("Please ensure the Nifty 500 stock list is loaded correctly.")
else:
    st.info("Click 'Run Screener' to start scanning all Nifty 500 stocks.")
    st.write("Stocks in Uptrend:", results)