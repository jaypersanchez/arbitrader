from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QSpacerItem, QSizePolicy,
                             QGridLayout, QGroupBox, QApplication)
import sys
import threading
from .strategies.scalping import ScalpingStrategy
from .strategies.arbitrage import ArbitrageStrategy
from .strategies.trend_following import TrendFollowingStrategy
from .strategies.mean_reversion import MeanReversionStrategy

class StrategyManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.strategy = None
        self.arbitrage_strategy = ArbitrageStrategy()
        self.active_strategies = {}

    def init_ui(self):
        # Create the main layout
        layout = QGridLayout()

        # Strategy Selection Group
        strategy_group = QGroupBox("Strategy Selection")
        strategy_layout = QGridLayout()

        strategy_layout.addWidget(QLabel("Select Strategy"), 0, 0)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Scalping", "Arbitrage", "Trend Following", "Mean Reversion"])
        self.strategy_combo.currentIndexChanged.connect(self.update_parameters)
        strategy_layout.addWidget(self.strategy_combo, 0, 1)

        strategy_layout.addWidget(QLabel("Parameters"), 1, 0)
        self.param_input = QLineEdit()
        self.param_input.setPlaceholderText("Enter parameters separated by commas")
        strategy_layout.addWidget(self.param_input, 1, 1)

        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group, 0, 0, 1, 2)

        # Description Group
        description_group = QGroupBox("Strategy Description")
        description_layout = QVBoxLayout()

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        description_layout.addWidget(self.description_text)

        description_group.setLayout(description_layout)
        layout.addWidget(description_group, 1, 0, 1, 2)

        # Start Button
        self.start_button = QPushButton("Start Strategy")
        self.start_button.clicked.connect(self.start_strategy)
        layout.addWidget(self.start_button, 2, 0, 1, 1)

        # Output Section
        layout.addWidget(QLabel("Output"), 3, 0)
        self.arbitrage_output = QTextEdit()
        self.arbitrage_output.setReadOnly(True)
        layout.addWidget(self.arbitrage_output, 4, 0, 1, 2)

        self.setLayout(layout)
        self.update_parameters()

    def update_parameters(self):
        selected_strategy = self.strategy_combo.currentText()
        if selected_strategy == "Scalping":
            self.param_input.setPlaceholderText("Enter trade amount and time frame")
            self.description_text.setPlainText("Scalping involves making numerous trades to profit from small price changes.")
        elif selected_strategy == "Arbitrage":
            self.param_input.setPlaceholderText("Enter asset pairs and price difference")
            self.description_text.setPlainText("Arbitrage involves taking advantage of price differences between markets.")
        elif selected_strategy == "Trend Following":
            self.param_input.setPlaceholderText("Enter trend indicators and thresholds")
            self.description_text.setPlainText("Trend following strategies aim to capture gains through the analysis of an asset's momentum.")
        elif selected_strategy == "Mean Reversion":
            self.param_input.setPlaceholderText("Enter mean reversion parameters")
            self.description_text.setPlainText("Mean reversion strategies assume that prices will revert to their historical mean.")

    def start_strategy(self):
        print("Start Strategy button pressed.")
        selected_strategy = self.strategy_combo.currentText()
        parameters = self.param_input.text().strip().split(',')

        if selected_strategy == "Scalping":
            self.strategy = ScalpingStrategy()
            print("Scalping strategy initialized.")
        elif selected_strategy == "Arbitrage":
            try:
                # Parse trading pairs (first parameter might contain spaces)
                trading_pairs = parameters[0].strip().split()
                min_profit_threshold = float(parameters[1].strip()) if len(parameters) > 1 else 0.01
                trade_amount = float(parameters[2].strip()) if len(parameters) > 2 else 100.0
                execution_interval = int(parameters[3].strip()) if len(parameters) > 3 else 60

                def update_output(message):
                    self.arbitrage_output.append(message)
                    # Scroll to the bottom
                    self.arbitrage_output.verticalScrollBar().setValue(
                        self.arbitrage_output.verticalScrollBar().maximum()
                    )

                self.strategy = ArbitrageStrategy(
                    trading_pairs=trading_pairs,
                    min_profit_threshold=min_profit_threshold,
                    trade_amount=trade_amount,
                    execution_interval=execution_interval,
                    output_callback=update_output
                )
                
                update_output("Arbitrage strategy initialized with parameters:")
                update_output(f"Trading pairs: {trading_pairs}")
                update_output(f"Min profit threshold: {min_profit_threshold}")
                update_output(f"Trade amount: {trade_amount}")
                update_output(f"Execution interval: {execution_interval}")
                
                threading.Thread(target=self.strategy.execute, daemon=True).start()
                update_output("Starting Arbitrage strategy...")
            except Exception as e:
                print(f"Error initializing arbitrage strategy: {e}")
                self.arbitrage_output.append(f"Error: {str(e)}")
                return
        elif selected_strategy == "Trend Following":
            self.strategy = TrendFollowingStrategy()
            print("Trend Following strategy initialized.")
        elif selected_strategy == "Mean Reversion":
            self.strategy = MeanReversionStrategy()
            print("Mean Reversion strategy initialized.")

        if self.strategy:
            print(f"{selected_strategy} strategy started.")

    def add_strategy(self, name, parameters):
        self.active_strategies[name] = parameters

    def remove_strategy(self, name):
        if name in self.active_strategies:
            del self.active_strategies[name]

    def get_active_strategies(self):
        return self.active_strategies

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StrategyManagement()
    window.show()
    sys.exit(app.exec_())
