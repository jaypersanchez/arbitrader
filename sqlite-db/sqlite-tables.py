import sqlite3

# Create SQLite database
conn = sqlite3.connect('trading_data.db')
cursor = conn.cursor()

# Create table for KuCoin price data
cursor.execute('''
CREATE TABLE IF NOT EXISTS kucoin_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    bid REAL,
    ask REAL,
    volume REAL,
    quote_volume REAL,
    timestamp INTEGER
)
''')

conn.commit()
print("Table created successfully!")
