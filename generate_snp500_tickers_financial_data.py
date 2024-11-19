# Goes over SNP500 tickers and computes growth for 5 year and 10 year periods as listed in code.
# Also fetches market cap and earnings data for the tickers in SNP500 index.
# Computes SNP500 (VOO) and Nasdaq100 (QQQ) outperformers.
# Dumps the data in different csv files:
#    - stock_tickers_data.csv
#    - snp500_outperformers.csv
#    - qqq_outperformers.csv

import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import time

# Define the 5-year and 10-year periods starting at 1994 and ending at 2024
# 5 year periods from 1994 onwards
five_year_periods = {
    "1994-1999": ("1994-01-01", "1999-01-01"),
    "1999-2004": ("1999-01-01", "2004-01-01"),
    "2004-2009": ("2004-01-01", "2009-01-01"),
    "2009-2014": ("2009-01-01", "2014-01-01"),
    "2014-2019": ("2014-01-01", "2019-01-01"),
    "2019-2024": ("2019-01-01", "2024-10-22")
}
# 10 year periods from 1994 onwards
ten_year_periods = {
    "1994-2004": ("1994-01-01", "2004-01-01"),
    "2004-2014": ("2004-01-01", "2014-01-01"),
    "2014-2024": ("2014-01-01", "2024-10-22")
}

# Sample tickers
sample_tickers_1 = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "BEP", "SPY"]
sample_tickers_2 = ["APH", "AXON", "CTAS", "DECK", "DHI", "FICO", "IT",
                    "KLAC", "MPWR", "MCO", "ORLY", "ODFL", "TT", "TDG",
                    "ADBE", "AMD", "GOOG", "GOOGL", "AMZN", "AAPL", "AMAT",
                    "AVGO", "COST", "ISRG", "INTU", "LLY", "MSFT", "NVDA", "NOW"]
sample_tickers_3 = ["FICO", "AXON", "KLAC", "MPWR", "CTAS", "TDG", "ODFL", "ORLY"]
sample_tickers_4 = [
    "QQQ", "ACN", "GOOGL", "GOOG", "AMZN", "APH", "ADI", "AAPL", "AJG", "AZO",
    "AXON", "AVGO", "CDNS", "CAT", "CBRE", "CTAS", "CPRT", "COST", "DHR", "DECK",
    "DE", "DXCM", "DHI", "EQIX", "ERIE", "FICO", "FI", "FTNT", "GRMN", "IT",
    "HD", "IDXX", "PODD", "INTU", "ISRG", "JBL", "KLAC", "LRCX", "LOW", "MAR",
    "MMC", "MAS", "MA", "MTD", "MOH", "MPWR", "MCO", "MSI", "MSCI", "NFLX",
    "NVDA", "NVR", "NXPI", "ORLY", "ODFL", "PKG", "POOL", "RJF", "SPGI", "NOW",
    "SHW", "TER", "TSLA", "TMO", "TJX", "TT", "TDG", "TYL", "UNH", "VRSK", "VRTX", "WST",
    "ADBE", "AMD", "GOOG", "GOOGL", "AMZN", "AAPL", "AMAT",
    "AVGO", "COST", "ISRG", "INTU", "LLY", "MSFT", "NVDA", "NOW"]

# SPY and QQQ ticker constants
snp500_ticker = 'SPY'
qqq_ticker = 'QQQ'

# Function to scrape the S&P 500 tickers from Wikipedia
def get_snp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})  # Find the correct table

    tickers = []
    for row in table.findAll('tr')[1:]:  # Skip the header row
        ticker = row.findAll('td')[0].text.strip()
        tickers.append(ticker)

    return tickers


# Function to calculate growth rate accounting for dividends
def calculate_growth_rate(start_price, end_price):
    return ((end_price - start_price) / start_price) * 100


# Function to format numbers in millions or billions with $ notation
def format_currency(value):
    if value is None:
        return "N/A"
    if value >= 1e9:
        return f"${value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.2f}M"
    else:
        return f"${value:.2f}"


# Function to format percentage with 2 decimal points
def format_percentage(value):
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


# Function to fetch growth rates, earnings, market cap, and revenue for a list of tickers
def fetch_growth_and_financials(tickers):
    financial_data = []

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        result = {"Ticker": ticker}

        # Get latest earnings, market cap, and revenue
        try:
            earnings = stock.financials.loc['Net Income'].iloc[0]  # Latest earnings
            market_cap = stock.info.get('marketCap', None)  # Market cap
            revenue = stock.financials.loc['Total Revenue'].iloc[0]  # Total revenue
            print(
                f"Fetched financial data for {ticker}: Earnings={earnings}, Market Cap={market_cap}, Revenue={revenue}")
        except Exception as e:
            print(f"Error fetching earnings/market cap/revenue for {ticker}: {e}")
            earnings = None
            market_cap = None
            revenue = None

        result['Latest Revenue'] = format_currency(revenue)
        result['Latest Earnings'] = format_currency(earnings)
        result['Market Cap'] = format_currency(market_cap)

        # Fetch growth rates for each period
        for period_name, (start_date, end_date) in five_year_periods.items():
            try:
                data = stock.history(start=start_date, end=end_date)

                if data.empty:
                    print(f"No data found for {ticker} in period {period_name}.")
                    result[period_name] = None
                    continue

                start_price = data["Close"].iloc[0]
                end_price = data["Close"].iloc[-1]
                growth_rate = calculate_growth_rate(start_price, end_price)
                result[period_name] = format_percentage(growth_rate)
                print(
                    f"{ticker} - {period_name}: Start Price = {start_price}, End Price = {end_price}, Growth = {growth_rate}%")

            except Exception as e:
                print(f"Error fetching data for {ticker} in period {period_name}: {e}")
                result[period_name] = None

        financial_data.append(result)

    return financial_data


# Function to compare growth rates with a benchmark (e.g., S&P 500 or QQQ) and find outperformers
def find_outperformers(stock_data, benchmark_data):
    outperformers = []
    for stock in stock_data:
        ticker = stock["Ticker"]
        if all(stock[period] is not None and benchmark_data[period] is not None and stock[period] > benchmark_data[
            period]
               for period in five_year_periods.keys()):
            outperformers.append(ticker)
    return outperformers


# Measure start time
start_time = time.time()
print(f"Program start time: {start_time:.2f} seconds")

# Fetch tickers and calculate their growth rates, earnings, market cap, and revenue
stock_tickers = sample_tickers_4
stock_tickers.insert(0, qqq_ticker)
stock_tickers.insert(0, snp500_ticker)
stock_tickers_data = fetch_growth_and_financials(stock_tickers)

# Fetch SNP 500 and QQQ growth rates
snp500_data = fetch_growth_and_financials([snp500_ticker])[0]
qqq_data = fetch_growth_and_financials([qqq_ticker])[0]

# Find outperformers for both SNP 500 and QQQ
snp500_outperformers = find_outperformers(stock_tickers_data, snp500_data)
qqq_outperformers = find_outperformers(stock_tickers_data, qqq_data)

# Convert data to DataFrame for better readability
stock_tickers_df = pd.DataFrame(stock_tickers_data)
snp500_outperformers_df = pd.DataFrame(snp500_outperformers, columns=["Ticker"])
qqq_outperformers_df = pd.DataFrame(qqq_outperformers, columns=["Ticker"])

# Save the growth rates, earnings, market cap, revenue, and outperformers to CSV files.
# TODO: Replace with actual paths
stock_tickers_df.to_csv("~/stock_tickers_data.csv", index=False)
snp500_outperformers_df.to_csv("~/snp500_outperformers.csv", index=False)
qqq_outperformers_df.to_csv("~/qqq_outperformers.csv", index=False)

# Print the DataFrames
print("Stock Financial and Growth Data:")
print(stock_tickers_df)
print("\nS&P 500 Outperformers (for all periods):")
print(snp500_outperformers_df)
print("\nQQQ Outperformers (for all periods):")
print(qqq_outperformers_df)

# Print the execution time
print(f"Program execution time: {time.time() - start_time:.2f} seconds")