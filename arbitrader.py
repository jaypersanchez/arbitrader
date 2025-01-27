import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QHBoxLayout, QMenuBar, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import ccxt
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables
load_dotenv()

class BalanceFetcher(QThread):
    update_balances = pyqtSignal(dict)

    def run(self):
        # Initialize KuCoin Exchange
        api_key = os.getenv("KUCOIN_API_KEY")
        api_secret = os.getenv("KUCOIN_SECRET_KEY")
        api_passphrase = os.getenv("KUCOIN_PASSPHRASE")

        exchange = ccxt.kucoin({
            'apiKey': api_key,
            'secret': api_secret,
            'password': api_passphrase,
            'enableRateLimit': True,
        })

        # Fetch balances for all accounts
        account_types = ['main', 'trading', 'margin', 'futures']
        balances = {}

        for account_type in account_types:
            try:
                balance = exchange.fetch_balance(params={'type': account_type})
                usdt_balance = balance['total'].get('USDT', 0)
                balances[account_type] = usdt_balance
            except Exception as e:
                print(f"An error occurred while fetching {account_type} balance: {str(e)}")
                balances[account_type] = 0

        self.update_balances.emit(balances)

class TradingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title
        self.setWindowTitle("AI Trading Agent")

        # Maximize window based on screen size
        self.setGeometry(0, 0, QApplication.primaryScreen().geometry().width(),
                         QApplication.primaryScreen().geometry().height())

        # Add Menu Bar for additional functionality
        self.menu_bar = self.menuBar()
        self.add_menu_actions()

        # Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Start fetching balances on startup
        self.loading_label = QLabel("Loading balances, please wait...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(self.loading_label, "Loading")
        self.fetch_balances()

        # Add other tabs after fetching balances
        self.tabs.addTab(self.create_strategy_management_tab(), "Strategy Management")
        self.tabs.addTab(self.create_backtesting_tab(), "Backtesting")
        self.tabs.addTab(self.create_risk_management_tab(), "Risk Management")

    def add_menu_actions(self):
        # File Menu
        file_menu = self.menu_bar.addMenu("File")

        # Exit Action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close_app)
        file_menu.addAction(exit_action)

        # Window Menu
        window_menu = self.menu_bar.addMenu("Window")

        # Minimize Action
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut("Ctrl+M")
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)

        # Maximize Action
        maximize_action = QAction("Maximize", self)
        maximize_action.setShortcut("Ctrl+Shift+M")
        maximize_action.triggered.connect(self.showMaximized)
        window_menu.addAction(maximize_action)

    def fetch_balances(self):
        self.thread = BalanceFetcher()
        self.thread.update_balances.connect(self.display_balances)
        self.thread.start()

    def display_balances(self, balances):
        # Remove loading label and display balances
        self.tabs.removeTab(self.tabs.indexOf(self.loading_label))

        # Prepare data for table
        table_data = [["Account Type", "USDT Balance"]] + [[account_type.capitalize() + " Account", balances[account_type]] for account_type in ['main', 'trading', 'margin', 'futures']]

        # Create a new tab for displaying balances
        balance_tab = QWidget()
        layout = QVBoxLayout()
        account_table = QTableWidget(len(table_data), 2)
        account_table.setHorizontalHeaderLabels(["Account Type", "USDT Balance"])

        for i, (account_type, usdt_balance) in enumerate(table_data[1:]):  # Skip header
            account_table.setItem(i, 0, QTableWidgetItem(account_type))
            account_table.setItem(i, 1, QTableWidgetItem(f"{usdt_balance:.2f}"))

        layout.addWidget(account_table)
        balance_tab.setLayout(layout)

        self.tabs.addTab(balance_tab, "Account Overview")
        self.tabs.setCurrentWidget(balance_tab)

    def close_app(self):
        # Gracefully close the application
        print("Exiting application...")
        self.close()

    def create_strategy_management_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Strategy"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Arbitrage", "Market Making", "Momentum-Based"])
        layout.addWidget(self.strategy_combo)

        layout.addWidget(QLabel("Parameters"))
        self.param_input = QLineEdit()
        layout.addWidget(self.param_input)

        start_button = QPushButton("Start Strategy")
        layout.addWidget(start_button)

        tab.setLayout(layout)
        return tab

    def create_backtesting_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Pair for Backtesting"))
        self.pair_input = QLineEdit()
        layout.addWidget(self.pair_input)

        layout.addWidget(QLabel("Select Date Range"))
        self.date_range_input = QLineEdit()
        layout.addWidget(self.date_range_input)

        run_button = QPushButton("Run Backtesting")
        layout.addWidget(run_button)

        tab.setLayout(layout)
        return tab

    def create_risk_management_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Set Maximum Trade Size (%)"))
        self.trade_size_input = QLineEdit()
        layout.addWidget(self.trade_size_input)

        layout.addWidget(QLabel("Enable Stop-Loss (Optional)"))
        self.stop_loss_input = QLineEdit()
        layout.addWidget(self.stop_loss_input)

        layout.addWidget(QLabel("Enable Take-Profit (Optional)"))
        self.take_profit_input = QLineEdit()
        layout.addWidget(self.take_profit_input)

        save_button = QPushButton("Save Risk Settings")
        layout.addWidget(save_button)

        tab.setLayout(layout)
        return tab


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingApp()
    window.showMaximized()  # Start maximized
    sys.exit(app.exec_())
