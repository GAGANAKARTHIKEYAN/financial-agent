import streamlit as st
import requests
import yfinance as yf
import pycountry
import os
from dotenv import load_dotenv

# =========================
# Load Environment
# =========================
load_dotenv()
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")

# =========================
# Major Stock Index Mapping
# =========================
index_mapping = {
    "India": ("INR", "National Stock Exchange of India", "^NSEI"),
    "Japan": ("JPY", "Tokyo Stock Exchange", "^N225"),
    "United States": ("USD", "New York Stock Exchange", "^GSPC"),
    "United Kingdom": ("GBP", "London Stock Exchange", "^FTSE"),
    "China": ("CNY", "Shanghai Stock Exchange", "000001.SS"),
    "South Korea": ("KRW", "Korea Exchange", "^KS11"),
    "Germany": ("EUR", "Frankfurt Stock Exchange", "^GDAXI"),
    "France": ("EUR", "Euronext Paris", "^FCHI"),
    "Canada": ("CAD", "Toronto Stock Exchange", "^GSPTSE"),
    "Australia": ("AUD", "Australian Securities Exchange", "^AXJO"),
}

# =========================
# Function: Get Currency Code Automatically
# =========================
def get_currency_code(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        currency = pycountry.currencies.get(numeric=country.numeric)
        return currency.alpha_3
    except:
        return None

# =========================
# Function: Get Exchange Rates
# =========================
def get_exchange_rates(currency):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{currency}"
    response = requests.get(url).json()

    if response.get("result") != "success":
        return None

    rates = response["conversion_rates"]

    return {
        "USD": rates.get("USD"),
        "INR": rates.get("INR"),
        "GBP": rates.get("GBP"),
        "EUR": rates.get("EUR"),
    }

# =========================
# Function: Get Stock Data
# =========================
def get_stock_data(country):
    if country not in index_mapping:
        return None

    currency, exchange, index_symbol = index_mapping[country]

    ticker = yf.Ticker(index_symbol)
    hist = ticker.history(period="1d")

    if hist.empty:
        return None

    price = hist["Close"].iloc[-1]

    return exchange, index_symbol, price

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Financial Intelligence Agent", layout="wide")
st.title("🌍 Global Financial Intelligence Agent")

country_input = st.text_input(
    "Enter Country Name",
    placeholder="Example: India, Japan, Argentina, UK..."
)

if st.button("Get Financial Details") and country_input:

    st.markdown(f"## 📊 Financial Details for {country_input.title()}")

    # -------------------------
    # Currency
    # -------------------------
    currency_code = get_currency_code(country_input)

    if currency_code:
        rates = get_exchange_rates(currency_code)

        if rates:
            st.subheader("💰 Official Currency")
            st.write(f"Currency: {currency_code}")

            st.subheader("💱 Exchange Rates")
            st.write(f"1 {currency_code} → USD: {rates['USD']}")
            st.write(f"1 {currency_code} → INR: {rates['INR']}")
            st.write(f"1 {currency_code} → GBP: {rates['GBP']}")
            st.write(f"1 {currency_code} → EUR: {rates['EUR']}")
        else:
            st.error("Exchange rate data not available.")
    else:
        st.error("Could not detect currency for this country.")

    # -------------------------
    # Stock Exchange
    # -------------------------
    stock_data = get_stock_data(country_input.title())

    if stock_data:
        exchange, symbol, price = stock_data

        st.subheader("📈 Major Stock Exchange")
        st.write(f"Exchange: {exchange}")
        st.write(f"Index Symbol: {symbol}")
        st.write(f"Current Index Value: {price}")
    else:
        st.warning("Stock index not mapped for this country.")

    # -------------------------
    # Google Maps
    # -------------------------
    st.subheader("📍 Stock Exchange Location")

    maps_query = f"{country_input} Stock Exchange"
    maps_link = f"https://www.google.com/maps/search/{maps_query}"

    st.markdown(f"[Open in Google Maps]({maps_link})")

    # Embedded Map (No API Key Needed)
    embed_url = f"https://www.google.com/maps?q={maps_query}&output=embed"

    st.components.v1.iframe(
        embed_url,
        height=500
    )
