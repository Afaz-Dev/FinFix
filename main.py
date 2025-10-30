from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox
)
from PyQt5.QtGui import QColor, QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_HALF_UP
import csv, sys
from pathlib import Path

DATA_DIR = Path("data")
LEDGER_CSV = DATA_DIR / "transactions.csv"
HEADER = ["tx_id", "type", "amount_rm", "desc"]

DARK_STYLESHEET = """
QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI'; }
QLineEdit { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QListWidget { background-color: #1C1C1C; border: 1px solid #333333; border-radius: 8px; }
QPushButton#themeButton { background-color: #323232; border: 1px solid #4A4A4A; border-radius: 8px; padding: 6px 12px; color: #E0E0E0; }
QPushButton#themeButton:hover { background-color: #3C3C3C; }
""".strip()

LIGHT_STYLESHEET = """
QWidget { background-color: #F5F5F5; color: #212121; font-family: 'Segoe UI'; }
QLineEdit { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QListWidget { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; }
QPushButton#themeButton { background-color: #E0E0E0; border: 1px solid #BDBDBD; border-radius: 8px; padding: 6px 12px; color: #212121; }
QPushButton#themeButton:hover { background-color: #D5D5D5; }
""".strip()

def money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def ensure_ledger():
    DATA_DIR.mkdir(exist_ok=True)
    if not LEDGER_CSV.exists():
        with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADER)

def next_tx_id() -> str:
    if not LEDGER_CSV.exists():
        return "TX001"
    with LEDGER_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return "TX001"
    last = rows[-1]["tx_id"][2:]  # after 'TX'
    return f"TX{int(last)+1:03d}"

class BudgetTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Budget Tracker")
        self.setGeometry(200, 200, 420, 560)
        self.theme_mode = "dark"
        ensure_ledger()

        # --- Layout
        layout = QVBoxLayout(self)

        title = QLabel("Student Budget Tracker")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.theme_btn = QPushButton("Switch to Light Mode")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        self.balance = Decimal("0.00")
        self.balance_label = QLabel("Balance: RM 0.00")
        self.balance_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.balance_label)

        # Inputs
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (e.g., 50.00)")
        v = QDoubleValidator(0.01, 1_000_000.0, 2)  # min, max, decimals
        self.amount_input.setValidator(v)
        layout.addWidget(self.amount_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Lunch, Books)")
        layout.addWidget(self.desc_input)

        # Buttons
        btn_layout = QHBoxLayout()
        self.income_btn = self.createGradientButton("Add Income", "#4CAF50", "#2E7D32")
        self.expense_btn = self.createGradientButton("Add Expense", "#E91E63", "#880E4F")
        btn_layout.addWidget(self.income_btn); btn_layout.addWidget(self.expense_btn)
        layout.addLayout(btn_layout)

        # List
        self.transaction_list = QListWidget()
        layout.addWidget(self.transaction_list)

        # Connect
        self.income_btn.clicked.connect(lambda: self.add_tx("income"))
        self.expense_btn.clicked.connect(lambda: self.add_tx("expense"))

        self.apply_theme()

        # Load existing
        self.load_ledger()
        self.update_balance()

    def createGradientButton(self, text, color1, color2):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:1 {color2});
                border: none; color: white; border-radius: 10px; padding: 8px 15px;
                font-weight: bold; font-size: 12pt;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,160)); shadow.setOffset(0,3)
        btn.setGraphicsEffect(shadow)
        return btn

    def load_ledger(self):
        self.transaction_list.clear()
        self.balance = Decimal("0.00")
        if not LEDGER_CSV.exists():
            return
        with LEDGER_CSV.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                amt = money(row["amount_rm"])
                sign = "+" if row["type"] == "income" else "-"
                if row["type"] == "income":
                    self.balance += amt
                else:
                    self.balance -= amt
                self.transaction_list.addItem(f"{sign} RM{amt:.2f} | {row['desc']}  ({row['tx_id']})")

    def add_tx(self, ttype: str):
        amt_text = self.amount_input.text().strip()
        if not amt_text:
            QMessageBox.warning(self, "Missing", "Amount is required.")
            return
        try:
            amt = money(amt_text)
            if amt <= 0:
                raise ValueError
        except Exception:
            QMessageBox.critical(self, "Invalid", "Enter a valid amount, e.g. 12.50")
            return

        desc = self.desc_input.text().strip() or "No description"
        txid = next_tx_id()

        # Update balance
        if ttype == "income":
            self.balance += amt
            prefix = "+"
        else:
            self.balance -= amt
            prefix = "-"

        # Append to CSV
        with LEDGER_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([txid, ttype, f"{amt:.2f}", desc])

        # UI update
        self.transaction_list.addItem(f"{prefix} RM{amt:.2f} | {desc}  ({txid})")
        self.update_balance()
        self.clear_inputs()

    def update_balance(self):
        self.balance_label.setText(f"Balance: RM {self.balance:.2f}")
        self.balance_label.setStyleSheet("color: #81C784;" if self.balance >= 0 else "color: #E57373;")

    def clear_inputs(self):
        self.amount_input.clear()
        self.desc_input.clear()
        self.amount_input.setFocus()

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme()
        self.update_balance()

    def apply_theme(self):
        if self.theme_mode == "dark":
            stylesheet = DARK_STYLESHEET
            button_text = "Switch to Light Mode"
        else:
            stylesheet = LIGHT_STYLESHEET
            button_text = "Switch to Dark Mode"
        self.setStyleSheet(stylesheet)
        self.theme_btn.setText(button_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BudgetTracker()
    win.show()
    sys.exit(app.exec_())
