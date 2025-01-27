import sys
import os

# Add the arbitrader directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QLineEdit, QComboBox, QHBoxLayout, QMenuBar, QAction
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import ccxt
from dotenv import load_dotenv
from tabulate import tabulate
from modules.strategy_management import StrategyManagement  # Import your StrategyManagement class

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
        self.setWindowTitle("AI Trading Agent")
        self.setGeometry(0, 0, QApplication.primaryScreen().geometry().width(),
                         QApplication.primaryScreen().geometry().height())

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Add Menu Bar
        self.menu_bar = self.menuBar()
        self.add_menu_actions()

        # Add balance display
        self.loading_label = QLabel("Loading balances, please wait...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.loading_label)
        self.fetch_balances()

        # Add Strategy Management
        self.strategy_management = StrategyManagement()
        self.main_layout.addWidget(self.strategy_management)

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
        # Remove loading label
        self.loading_label.setParent(None)

        # Create balance display widget
        balance_widget = QWidget()
        balance_layout = QVBoxLayout()
        
        # Create and setup table
        account_table = QTableWidget(4, 2)
        account_table.setHorizontalHeaderLabels(["Account Type", "USDT Balance"])
        
        for i, (account_type, balance) in enumerate([
            ('Main', balances['main']),
            ('Trading', balances['trading']),
            ('Margin', balances['margin']),
            ('Futures', balances['futures'])
        ]):
            account_table.setItem(i, 0, QTableWidgetItem(f"{account_type} Account"))
            account_table.setItem(i, 1, QTableWidgetItem(f"{balance:.2f}"))

        balance_layout.addWidget(account_table)
        balance_widget.setLayout(balance_layout)
        
        # Add to main layout
        self.main_layout.insertWidget(0, balance_widget)

    def close_app(self):
        # Gracefully close the application
        print("Exiting application...")
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingApp()
    window.showMaximized()  # Start maximized
    sys.exit(app.exec_())
