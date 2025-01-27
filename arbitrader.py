import ccxt
import os
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()

# API Credentials
api_key = os.getenv("KUCOIN_API_KEY")
api_secret = os.getenv("KUCOIN_SECRET_KEY")
api_passphrase = os.getenv("KUCOIN_PASSPHRASE")

# Initialize KuCoin Exchange
exchange = ccxt.kucoin({
    'apiKey': api_key,
    'secret': api_secret,
    'password': api_passphrase,
    'enableRateLimit': True,
})

# Fetch balances for all accounts
try:
    # Fetch balances for all accounts
    account_types = ['main', 'trading', 'margin', 'futures']  # List of valid account types
    balances = {}

    for account_type in account_types:
        try:
            # Check if the account type is supported before fetching
            if account_type == 'margin' and not margin_enabled:  # Replace with your logic to check if margin is enabled
                print("Margin trading is not enabled.")
                balances[account_type] = 0
                continue
            
            balance = exchange.fetch_balance(params={'type': account_type})
            balances[account_type] = balance['total']['USDT']  # Adjusted to fetch total balance
        except Exception as e:
            print(f"An error occurred while fetching {account_type} balance: {str(e)}")
            balances[account_type] = 0  # Default to 0 if there's an error

    # Prepare data for table, including all balances
    table_data = [["Account Type", "USDT Balance"]] + [[account_type.capitalize() + " Account", balances[account_type]] for account_type in account_types]

    # Print balances in table format
    print(tabulate(table_data, headers="firstrow", tablefmt="grid"))

except Exception as e:
    print("An error occurred:", str(e))
