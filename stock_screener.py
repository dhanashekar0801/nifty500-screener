import pandas as pd
import yfinance as yf
import ta
import streamlit as st

# Set Streamlit page config
st.set_page_config(page_title='Nifty 500 Stock Screener', layout='wide')

# Define Nifty 500 stock symbols (for demo, we'll use a few symbols)
nifty500_symbols = ['TCS.NS', 'RELIANCE.NS', 'INFY.NS', 'HDFC.NS', 'SBIN.NS']

# Function to fetch stock data
def fetch_stock_data(symbol):
    data = yf.download(symbol, period='6mo')
    return data

# Function to calculate indicators
def calculate_indicators(data):
    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    data['EMA_50'] = ta.trend.ema_indicator(data['Close'], window=50)
    data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
    return data

# Function to screen stocks
def screen_stocks(symbols):
    screened_stocks = []
    for symbol in symbols:
        data = fetch_stock_data(symbol)
        data = calculate_indicators(data)
        # Criteria: EMA crossover & RSI between 40-60
        if data['EMA_20'].iloc[-1] > data['EMA_50'].iloc[-1] and 40 < data['RSI'].iloc[-1] < 60:
            screened_stocks.append(symbol)
    return screened_stocks

# Display app title
st.title('Nifty 500 Stock Screener')

# Run screening and display results
if st.button('Run Screener'):
    st.write('Screening stocks...')
    results = screen_stocks(nifty500_symbols)
    if results:
        st.success(f'Suggested stocks: {results}')
    else:
        st.warning('No stocks met the criteria.')
