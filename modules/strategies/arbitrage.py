import ccxt
import time
import sqlite3

# Initialize KuCoin exchange
exchange = ccxt.kucoin()

class ArbitrageStrategy:
    def __init__(self, trading_pairs=None, min_profit_threshold=0.01, trade_amount=100.0, execution_interval=60, output_callback=None):
        """
        Initialize arbitrage strategy with parameters
        
        Args:
            trading_pairs (list): List of trading pairs to monitor (e.g., ["BTC/USDT", "ETH/USDT"])
            min_profit_threshold (float): Minimum price difference (in %) to execute trade
            trade_amount (float): Amount in USDT to trade
            execution_interval (int): How often to check for arbitrage opportunities (in seconds)
            output_callback (function): Callback function to handle output messages
        """
        self.trading_pairs = trading_pairs or ["BTC/USDT", "ETH/USDT"]
        self.min_profit_threshold = min_profit_threshold  # 1% minimum profit
        self.trade_amount = trade_amount
        self.execution_interval = execution_interval
        self.is_running = False
        self.output_callback = output_callback
        print("Initializing ArbitrageStrategy...")  # Debugging statement
        # Connect to the SQLite database
        self.conn = sqlite3.connect('trading_data.db')
        self.cursor = self.conn.cursor()
        self.data_fetched = False  # Flag to indicate if data has been fetched
        print("Database connection established.")  # Debugging statement

    def log(self, message):
        """Helper method to handle output"""
        print(message)  # Still print to console
        if self.output_callback:
            self.output_callback(message)  # Send to UI

    def fetch_and_save_data(self):
        print("Fetching and saving data...")  # Debugging statement
        try:
            # Fetch all markets from KuCoin
            markets = exchange.fetch_markets()
            symbols = [market['symbol'] for market in markets]
            print(f"Fetched {len(symbols)} trading pairs.")  # Debugging statement

            # Fetch ticker data for all trading pairs
            for symbol in symbols:
                print(f"Fetching ticker for {symbol}...")  # Debugging statement
                ticker = exchange.fetch_ticker(symbol)
                
                # Extract relevant data
                bid = ticker['bid']
                ask = ticker['ask']
                volume = ticker['baseVolume']
                quote_volume = ticker['quoteVolume']
                timestamp = ticker['timestamp']

                # Save data to SQLite
                self.cursor.execute(''' 
                    INSERT INTO kucoin_prices (symbol, bid, ask, volume, quote_volume, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (symbol, bid, ask, volume, quote_volume, timestamp))
                self.conn.commit()
                print(f"Data saved for {symbol}: Bid={bid}, Ask={ask}, Volume={volume}, Quote Volume={quote_volume}, Timestamp={timestamp}")  # Debugging statement

            self.data_fetched = True  # Set the flag to indicate data fetching is complete
            print("Data fetching complete.")  # Debugging statement

        except Exception as e:
            print(f"Error fetching data: {e}")  # Log any errors

    def analyze_triangular_arbitrage(self):
        print("Analyzing triangular arbitrage...")  # Debugging statement
        if not self.data_fetched:
            print("Data not fetched yet. Skipping analysis.")  # Debugging statement
            return  # Skip analysis if data hasn't been fetched

        # Define the target triangular arbitrage pairs
        pairs = [
            ("USDT/BTC", "BTC/ETH", "ETH/USDT"),
            ("BTC/ETH", "ETH/XRP", "XRP/BTC"),
            # Add more pairs as needed
        ]

        for pair1, pair2, pair3 in pairs:
            print(f"Checking arbitrage opportunity for pairs: {pair1}, {pair2}, {pair3}")  # Debugging statement
            try:
                # Fetch the latest prices from the database
                self.cursor.execute(f'''
                    SELECT bid, ask FROM kucoin_prices
                    WHERE symbol IN ("{pair1}", "{pair2}", "{pair3}")
                    ORDER BY timestamp DESC
                    LIMIT 1
                ''')
                prices = {row[0]: {'bid': row[1], 'ask': row[2]} for row in self.cursor.fetchall()}
                print(f"Fetched prices: {prices}")  # Debugging statement

                # Check for arbitrage opportunities
                if pair1 in prices and pair2 in prices and pair3 in prices:
                    usdt_to_btc = 1 / prices[pair1]['ask']
                    btc_to_eth = 1 / prices[pair2]['ask']
                    eth_to_usdt = prices[pair3]['bid']

                    # Calculate the final amount of USDT after the triangular arbitrage
                    final_usdt = usdt_to_btc * btc_to_eth * eth_to_usdt
                    print(f"Final USDT after arbitrage: {final_usdt:.4f}")  # Debugging statement

                    if final_usdt > 1:
                        profit = final_usdt - 1
                        print(f"Arbitrage Opportunity: Start with 1 USDT, end with {final_usdt:.4f} USDT. Profit: {profit:.4f} USDT")
                    else:
                        print("No arbitrage opportunity at the moment.")

                else:
                    print(f"Missing prices for pairs: {pair1}, {pair2}, {pair3}")  # Debugging statement

            except Exception as e:
                print(f"Error analyzing arbitrage: {e}")

    def execute(self):
        """Main execution loop for the arbitrage strategy"""
        self.is_running = True
        while self.is_running:
            try:
                self.log(f"\nChecking prices for pairs: {self.trading_pairs}")
                for pair in self.trading_pairs:
                    try:
                        ticker = exchange.fetch_ticker(pair)
                        self.log(f"{pair}: Bid: {ticker['bid']}, Ask: {ticker['ask']}")
                        
                        # Calculate potential profit
                        spread = (ticker['bid'] - ticker['ask']) / ticker['ask'] * 100
                        self.log(f"Current spread for {pair}: {spread:.2f}%")
                        
                        if spread > self.min_profit_threshold:
                            self.log(f"Profitable opportunity found! Spread: {spread:.2f}%")
                            potential_profit = self.trade_amount * (spread / 100)
                            self.log(f"Potential profit: {potential_profit:.2f} USDT")
                    except Exception as e:
                        self.log(f"Error checking {pair}: {str(e)}")
                
                self.log(f"Waiting {self.execution_interval} seconds before next check...")
                time.sleep(self.execution_interval)
                
            except Exception as e:
                self.log(f"Error in arbitrage execution: {str(e)}")
                time.sleep(5)  # Wait a bit before retrying

    def stop(self):
        """Stop the strategy execution"""
        self.is_running = False

    def close_connection(self):
        print("Closing database connection...")  # Debugging statement
        # Close the database connection when done
        self.conn.close()

if __name__ == "__main__":
    print("Starting the application...")  # Debugging statement
    app = QApplication(sys.argv)
    window = StrategyManagement()
    window.show()
    print("Application window shown.")  # Debugging statement
    sys.exit(app.exec_())
