from shiny import App, render, ui, reactive
import yfinance as yf
import pandas as pd

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist_data = stock.history(period="5y")

    # Check if 'Dividends' column is in the data
    if 'Dividends' in hist_data.columns:
        dividends = hist_data[['Dividends']].loc[hist_data['Dividends'] > 0]
    else:
        dividends = pd.DataFrame(columns=['Dividends'])  # Empty DataFrame if no dividends found
    
    return hist_data, dividends

def calculate_price_dividend_ratio(symbol):
    hist_data, dividends = get_stock_data(symbol)
    results = []
    for date, row in dividends.iterrows():
        dividend = row['Dividends']
        price = hist_data.loc[date]['Close'] if date in hist_data.index else None
        if price and dividend > 0:
            ratio = price / dividend
            results.append({
                "date": date,
                "dividend": dividend,
                "price": price,
                "price_dividend_ratio": ratio
            })
    return pd.DataFrame(results)

# Define the UI layout
app_ui = ui.page_fluid(
    ui.h2("Stock Dividend Evaluation"),
    ui.input_text("ticker", "Enter Stock Ticker", placeholder="AAPL"),
    ui.input_action_button("search_btn", "Search"),
    ui.output_table("results_table")
)

# Define server logic
def server(input, output, session):
    # Reactive value to hold the results DataFrame
    ticker_data = reactive.Value(pd.DataFrame())

    @reactive.Effect
    @reactive.event(input.search_btn)
    def calculate_and_store():
        ticker_symbol = input.ticker()
        if ticker_symbol:
            results_df = calculate_price_dividend_ratio(ticker_symbol)
            ticker_data.set(results_df)
        else:
            ticker_data.set(pd.DataFrame())  # Set empty DataFrame if no input

    # Render the table based on the reactive value
    @output
    @render.table
    def results_table():
        return ticker_data.get()  # Get the latest DataFrame stored in ticker_data

# Create and run the app
app = App(app_ui, server)
