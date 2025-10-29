from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QHBoxLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt
import sys


class BudgetTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Budget Tracker")
        self.setGeometry(200, 200, 400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: #1E1E1E;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 6px;
                color: #E0E0E0;
            }
            QListWidget {
                background-color: #1C1C1C;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)

        # --- Main Layout ---
        layout = QVBoxLayout()

        # --- Title ---
        title = QLabel("Student Budget Tracker 💰")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Balance Display ---
        self.balance_label = QLabel("Balance: RM 0.00")
        self.balance_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.balance_label)

        # --- Input Fields ---
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (e.g., 50.00)")
        layout.addWidget(self.amount_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Lunch, Books)")
        layout.addWidget(self.desc_input)

        # --- Buttons Layout ---
        btn_layout = QHBoxLayout()

        self.income_btn = self.createGradientButton("Add Income", "#4CAF50", "#2E7D32")
        self.expense_btn = self.createGradientButton("Add Expense", "#E91E63", "#880E4F")

        btn_layout.addWidget(self.income_btn)
        btn_layout.addWidget(self.expense_btn)
        layout.addLayout(btn_layout)

        # --- Transaction List ---
        self.transaction_list = QListWidget()
        layout.addWidget(self.transaction_list)

        # --- Data ---
        self.balance = 0.0

        # --- Connect Buttons ---
        self.income_btn.clicked.connect(self.add_income)
        self.expense_btn.clicked.connect(self.add_expense)

        # --- Set Layout ---
        self.setLayout(layout)

    # ---- Helper: Create Gradient Button ----
    def createGradientButton(self, text, color1, color2):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color1}, stop:1 {color2});
                border: none;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 3)
        btn.setGraphicsEffect(shadow)
        return btn

    # ---- Add Income ----
    def add_income(self):
        try:
            amount = float(self.amount_input.text())
            desc = self.desc_input.text() or "No description"
            self.balance += amount
            self.transaction_list.addItem(f"+ RM{amount:.2f} — {desc}")
            self.update_balance()
            self.clear_inputs()
        except ValueError:
            self.transaction_list.addItem("⚠ Invalid income input")

    # ---- Add Expense ----
    def add_expense(self):
        try:
            amount = float(self.amount_input.text())
            desc = self.desc_input.text() or "No description"
            self.balance -= amount
            self.transaction_list.addItem(f"- RM{amount:.2f} — {desc}")
            self.update_balance()
            self.clear_inputs()
        except ValueError:
            self.transaction_list.addItem("⚠ Invalid expense input")

    # ---- Update Balance ----
    def update_balance(self):
        self.balance_label.setText(f"Balance: RM {self.balance:.2f}")
        # Change color based on balance
        if self.balance >= 0:
            self.balance_label.setStyleSheet("color: #81C784;")
        else:
            self.balance_label.setStyleSheet("color: #E57373;")

    # ---- Clear Inputs ----
    def clear_inputs(self):
        self.amount_input.clear()
        self.desc_input.clear()


# ---- Main App Runner ----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BudgetTracker()
    window.show()
    sys.exit(app.exec_())
