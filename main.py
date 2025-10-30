from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox,
    QComboBox, QPlainTextEdit, QFileDialog, QDialog, QFrame, QSplitter, QDialogButtonBox
)
from PyQt5.QtGui import QColor, QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from datetime import date
import csv, os, shutil, sys, stat, importlib, json, time
from pathlib import Path

import requests

Figure = None
FigureCanvasQTAgg = None
MATPLOTLIB_AVAILABLE = False

try:
    matplotlib_figure = importlib.import_module("matplotlib.figure")
    matplotlib_backend = importlib.import_module("matplotlib.backends.backend_qt5agg")
    Figure = getattr(matplotlib_figure, "Figure", None)
    FigureCanvasQTAgg = getattr(matplotlib_backend, "FigureCanvasQTAgg", None)
    MATPLOTLIB_AVAILABLE = Figure is not None and FigureCanvasQTAgg is not None
except Exception:
    MATPLOTLIB_AVAILABLE = False

DATA_DIR = Path.home() / ".finfix_data"
LEGACY_DATA_DIR = Path("data")
LEDGER_CSV = DATA_DIR / "transactions.csv"
BUDGET_CSV = DATA_DIR / "budgets.csv"
LEGACY_LEDGER_CSV = LEGACY_DATA_DIR / "transactions.csv"
LEGACY_BUDGET_CSV = LEGACY_DATA_DIR / "budgets.csv"
LEDGER_HEADER = ["tx_id", "date", "type", "category", "amount_rm", "desc"]
OLD_LEDGER_HEADER = ["tx_id", "type", "amount_rm", "desc"]
BUDGET_HEADER = ["category", "monthly_budget_rm"]
CURRENCY_JSON = DATA_DIR / "rates.json"
RATES_TTL_SECONDS = 12 * 60 * 60  # reuse rates for half a day to limit network calls
RATES_API_URL = "https://open.er-api.com/v6/latest"
DEFAULT_TARGET_CURRENCIES = ["USD", "EUR", "GBP", "SGD", "AUD", "JPY", "CNY", "THB"]
FALLBACK_RATES = {
    "MYR": 1.0,
    "USD": 0.21,
    "EUR": 0.19,
    "GBP": 0.16,
    "SGD": 0.28,
    "AUD": 0.32,
    "JPY": 32.0,
    "CNY": 1.52,
    "THB": 7.4,
}
FALLBACK_NAMES = {
    "MYR": "Malaysian Ringgit",
    "USD": "US Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "SGD": "Singapore Dollar",
    "AUD": "Australian Dollar",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
    "THB": "Thai Baht",
    "IDR": "Indonesian Rupiah",
    "CAD": "Canadian Dollar",
    "CHF": "Swiss Franc",
    "NZD": "New Zealand Dollar",
    "HKD": "Hong Kong Dollar",
    "KRW": "South Korean Won",
    "INR": "Indian Rupee",
}

DARK_STYLESHEET = """
QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI'; }
QLineEdit { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QListWidget { background-color: #1C1C1C; border: 1px solid #333333; border-radius: 8px; }
QPushButton#themeButton { background-color: #323232; border: 1px solid #4A4A4A; border-radius: 8px; padding: 6px 12px; color: #E0E0E0; }
QPushButton#themeButton:hover { background-color: #3C3C3C; }
QPlainTextEdit { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QComboBox { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QFrame#HeaderBar { background-color: #1D1D28; border-radius: 18px; }
QLabel#Title { font-size: 20px; font-weight: 600; background-color: transparent; }
QLabel#Subtitle { color: #B0BEC5; font-size: 11px; background-color: transparent; }
QLabel#BalanceValue { background-color: #1E3A29; border-radius: 14px; padding: 8px 14px; font-size: 15px; font-weight: 600; color: #A5D6A7; }
QFrame#Card { background-color: #1A1A1F; border: 1px solid #2C2C34; border-radius: 16px; }
QLabel#SectionTitle { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #9FA8DA; background-color: transparent; }
QPushButton#SecondaryButton { background-color: #2A2A33; border: 1px solid #3A3A45; border-radius: 10px; padding: 9px 12px; font-weight: 600; color: #F5F5F5; }
QPushButton#SecondaryButton:hover { background-color: #353543; }
QLabel#InfoText { color: #B0BEC5; font-size: 11px; background-color: transparent; }
""".strip()

LIGHT_STYLESHEET = """
QWidget { background-color: #F5F5F5; color: #212121; font-family: 'Segoe UI'; }
QLineEdit { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QListWidget { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; }
QPushButton#themeButton { background-color: #E0E0E0; border: 1px solid #BDBDBD; border-radius: 8px; padding: 6px 12px; color: #212121; }
QPushButton#themeButton:hover { background-color: #D5D5D5; }
QPlainTextEdit { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QComboBox { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QFrame#HeaderBar { background-color: #FFFFFF; border-radius: 18px; border: 1px solid #E0E0E0; }
QLabel#Title { font-size: 20px; font-weight: 600; color: #1B5E20; background-color: transparent; }
QLabel#Subtitle { color: #5F6368; font-size: 11px; background-color: transparent; }
QLabel#BalanceValue { background-color: #E8F5E9; border-radius: 14px; padding: 8px 14px; font-size: 15px; font-weight: 600; color: #2E7D32; }
QFrame#Card { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 16px; }
QLabel#SectionTitle { font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #3949AB; background-color: transparent; }
QPushButton#SecondaryButton { background-color: #F0F0F0; border: 1px solid #D0D0D0; border-radius: 10px; padding: 9px 12px; font-weight: 600; color: #1F1F1F; }
QPushButton#SecondaryButton:hover { background-color: #E4E4E4; }
QLabel#InfoText { color: #5F6368; font-size: 11px; background-color: transparent; }
""".strip()

def money(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            os.chmod(path, 0o700)
        except Exception:
            pass
    else:
        try:
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs != -1 and attrs & FILE_ATTRIBUTE_HIDDEN == 0:
                ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs | FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            pass

def ensure_private_file(path: Path) -> None:
    if not path.exists():
        return
    ensure_writable(path)
    if os.name != "nt":
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass
    else:
        try:
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs != -1 and attrs & FILE_ATTRIBUTE_HIDDEN == 0:
                ctypes.windll.kernel32.SetFileAttributesW(str(path), attrs | FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            pass

def ensure_writable(path: Path) -> None:
    if not path.exists():
        return
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    except Exception:
        pass
    if os.name == "nt":
        try:
            import ctypes
            FILE_ATTRIBUTE_READONLY = 0x01
            FILE_ATTRIBUTE_HIDDEN = 0x02
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
            if attrs != -1:
                new_attrs = attrs & ~FILE_ATTRIBUTE_READONLY
                new_attrs &= ~FILE_ATTRIBUTE_HIDDEN
                if new_attrs != attrs:
                    ctypes.windll.kernel32.SetFileAttributesW(str(path), new_attrs)
        except Exception:
            pass

def migrate_ledger_schema() -> None:
    try:
        with LEDGER_CSV.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except FileNotFoundError:
        return

    if not rows:
        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(LEDGER_HEADER)
        ensure_private_file(LEDGER_CSV)
        return

    header = rows[0]
    if header == LEDGER_HEADER:
        ensure_private_file(LEDGER_CSV)
        return

    if header == OLD_LEDGER_HEADER:
        today_str = date.today().isoformat()
        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(LEDGER_HEADER)
            for row in rows[1:]:
                tx_id, ttype, amount_rm, desc = row
                writer.writerow([tx_id, today_str, ttype, "General", amount_rm, desc])
        ensure_private_file(LEDGER_CSV)
        return

    lower_header = {name.lower(): idx for idx, name in enumerate(header)}
    def fetch(row, key, default=""):
        idx = lower_header.get(key)
        if idx is None or idx >= len(row):
            return default
        return row[idx]

    today_str = date.today().isoformat()
    ensure_writable(LEDGER_CSV)
    with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(LEDGER_HEADER)
        for idx, row in enumerate(rows[1:], start=1):
            tx_id = fetch(row, "tx_id", f"TX{idx:03d}")
            ttype = fetch(row, "type", "expense")
            tx_date = fetch(row, "date", today_str)
            category = fetch(row, "category", "General")
            amount = fetch(row, "amount_rm", fetch(row, "amount", "0.00"))
            desc = fetch(row, "desc", fetch(row, "description", ""))
            writer.writerow([tx_id, tx_date, ttype, category or "General", amount, desc])
    ensure_private_file(LEDGER_CSV)

def ensure_storage() -> None:
    ensure_private_dir(DATA_DIR)
    if not LEDGER_CSV.exists():
        if LEGACY_LEDGER_CSV.exists():
            shutil.copyfile(LEGACY_LEDGER_CSV, LEDGER_CSV)
            ensure_private_file(LEDGER_CSV)
            migrate_ledger_schema()
        else:
            with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(LEDGER_HEADER)
            ensure_private_file(LEDGER_CSV)
    else:
        ensure_writable(LEDGER_CSV)
        migrate_ledger_schema()
    if not BUDGET_CSV.exists():
        if LEGACY_BUDGET_CSV.exists():
            shutil.copyfile(LEGACY_BUDGET_CSV, BUDGET_CSV)
            ensure_private_file(BUDGET_CSV)
        else:
            with BUDGET_CSV.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(BUDGET_HEADER)
            ensure_private_file(BUDGET_CSV)
    else:
        ensure_writable(BUDGET_CSV)
        ensure_private_file(BUDGET_CSV)
    if not CURRENCY_JSON.exists():
        ensure_writable(CURRENCY_JSON)
        with CURRENCY_JSON.open("w", encoding="utf-8") as f:
            json.dump({"base": "MYR", "timestamp": 0, "rates": FALLBACK_RATES}, f)
        ensure_private_file(CURRENCY_JSON)
    else:
        ensure_private_file(CURRENCY_JSON)


def load_cached_rates() -> dict:
    try:
        with CURRENCY_JSON.open(encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                rates = data.get("rates") or {}
                if isinstance(rates, dict):
                    for code, value in FALLBACK_RATES.items():
                        rates.setdefault(code, value)
                    data["rates"] = rates
                else:
                    data["rates"] = FALLBACK_RATES.copy()
                data.setdefault("base", "MYR")
                data.setdefault("timestamp", 0)
                return data
    except Exception:
        pass
    return {"base": "MYR", "timestamp": 0, "rates": FALLBACK_RATES.copy()}


def store_rates(data: dict) -> None:
    ensure_writable(CURRENCY_JSON)
    with CURRENCY_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    ensure_private_file(CURRENCY_JSON)

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
        self.setGeometry(200, 200, 520, 720)
        self.theme_mode = "dark"
        self.transactions = []
        self.categories = set()
        self.budget_map = {}
        self.balance = Decimal("0.00")
        ensure_storage()
        rate_snapshot = load_cached_rates()
        self.exchange_rates = rate_snapshot.get("rates", {"MYR": 1.0})
        self.base_currency = rate_snapshot.get("base", "MYR")
        self.rates_timestamp = rate_snapshot.get("timestamp", 0)
        self.selected_currency_code = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setSpacing(24)

        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        title_label = QLabel("Student Budget Tracker")
        title_label.setObjectName("Title")
        subtitle = QLabel("Track spending, budgets, and savings with a clear monthly view.")
        subtitle.setObjectName("Subtitle")
        title_container.addWidget(title_label)
        title_container.addWidget(subtitle)

        header_layout.addLayout(title_container)
        header_layout.addStretch(1)

        header_actions = QVBoxLayout()
        header_actions.setSpacing(8)
        header_actions.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.balance_label = QLabel("Net Position: RM 0.00")
        self.balance_label.setObjectName("BalanceValue")
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.theme_btn = QPushButton("Switch to Light Mode")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.clicked.connect(self.toggle_theme)

        header_actions.addWidget(self.balance_label)
        header_actions.addWidget(self.theme_btn, alignment=Qt.AlignmentFlag.AlignRight)

        header_layout.addLayout(header_actions)

        header_wrapper = QWidget()
        header_wrapper_layout = QVBoxLayout(header_wrapper)
        header_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        header_wrapper_layout.setSpacing(0)
        header_wrapper_layout.addWidget(header)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(12)
        tx_header = QLabel("Log Transaction")
        tx_header.setObjectName("SectionTitle")
        form_layout.addWidget(tx_header)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (e.g., 50.00)")
        self.amount_input.setValidator(QDoubleValidator(0.01, 1_000_000.0, 2))
        form_layout.addWidget(self.amount_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Lunch, Books)")
        form_layout.addWidget(self.desc_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.category_input.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.category_input.setMinimumContentsLength(12)
        line_edit = self.category_input.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText("Category (e.g., Food, Books, Savings)")
        form_layout.addWidget(self.category_input)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.income_btn = self.createGradientButton("Add Income", "#4CAF50", "#2E7D32")
        self.expense_btn = self.createGradientButton("Add Expense", "#E91E63", "#880E4F")
        self.savings_btn = self.createGradientButton("Log Savings", "#03A9F4", "#01579B")
        btn_layout.addWidget(self.income_btn)
        btn_layout.addWidget(self.expense_btn)
        btn_layout.addWidget(self.savings_btn)
        form_layout.addLayout(btn_layout)

        budget_card = QFrame()
        budget_card.setObjectName("Card")
        budget_layout = QVBoxLayout(budget_card)
        budget_layout.setContentsMargins(20, 20, 20, 20)
        budget_layout.setSpacing(12)
        budget_header = QLabel("Monthly Budgets")
        budget_header.setObjectName("SectionTitle")
        budget_layout.addWidget(budget_header)

        self.budget_category_input = QLineEdit()
        self.budget_category_input.setPlaceholderText("Category name (e.g., Food)")
        self.budget_amount_input = QLineEdit()
        self.budget_amount_input.setPlaceholderText("Monthly budget (RM)")
        self.budget_amount_input.setValidator(QDoubleValidator(0.00, 1_000_000.0, 2))
        budget_form = QHBoxLayout()
        budget_form.setSpacing(10)
        budget_form.addWidget(self.budget_category_input)
        budget_form.addWidget(self.budget_amount_input)
        self.add_budget_btn = QPushButton("Save Budget")
        self.add_budget_btn.setObjectName("SecondaryButton")
        budget_form.addWidget(self.add_budget_btn)
        budget_layout.addLayout(budget_form)

        self.budget_list = QListWidget()
        self.budget_list.setMinimumHeight(120)
        budget_layout.addWidget(self.budget_list)

        converter_card = QFrame()
        converter_card.setObjectName("Card")
        converter_layout = QVBoxLayout(converter_card)
        converter_layout.setContentsMargins(20, 20, 20, 20)
        converter_layout.setSpacing(12)
        converter_header = QLabel("Currency Converter")
        converter_header.setObjectName("SectionTitle")
        converter_layout.addWidget(converter_header)

        self.currency_amount_input = QLineEdit()
        self.currency_amount_input.setPlaceholderText("Amount in MYR")
        self.currency_amount_input.setValidator(QDoubleValidator(0.00, 1_000_000.0, 2))
        converter_layout.addWidget(self.currency_amount_input)

        self.currency_target_combo = QComboBox()
        self.currency_target_combo.setEditable(True)
        line_edit = self.currency_target_combo.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText("Search currency (e.g., USD - US Dollar)")
        converter_layout.addWidget(self.currency_target_combo)

        converter_buttons = QHBoxLayout()
        converter_buttons.setSpacing(10)
        self.currency_convert_btn = QPushButton("Convert")
        self.currency_convert_btn.setObjectName("SecondaryButton")
        self.currency_update_btn = QPushButton("Refresh Rates")
        self.currency_update_btn.setObjectName("SecondaryButton")
        converter_buttons.addWidget(self.currency_convert_btn)
        converter_buttons.addWidget(self.currency_update_btn)
        converter_layout.addLayout(converter_buttons)

        self.currency_result_label = QLabel("Result: -")
        self.currency_result_label.setWordWrap(True)
        converter_layout.addWidget(self.currency_result_label)

        self.currency_info_label = QLabel("Rates last updated: -")
        self.currency_info_label.setObjectName("InfoText")
        self.currency_info_label.setWordWrap(True)
        converter_layout.addWidget(self.currency_info_label)

        ledger_card = QFrame()
        ledger_card.setObjectName("Card")
        ledger_layout = QVBoxLayout(ledger_card)
        ledger_layout.setContentsMargins(20, 20, 20, 20)
        ledger_layout.setSpacing(12)
        ledger_header = QLabel("Transactions")
        ledger_header.setObjectName("SectionTitle")
        ledger_layout.addWidget(ledger_header)

        self.transaction_list = QListWidget()
        self.transaction_list.setMinimumHeight(220)
        ledger_layout.addWidget(self.transaction_list)

        reclass_row = QHBoxLayout()
        reclass_row.setSpacing(10)
        self.reclass_type_combo = QComboBox()
        self.reclass_type_combo.addItems(["income", "expense", "savings"])
        self.reclass_category_input = QLineEdit()
        self.reclass_category_input.setPlaceholderText("New category (optional)")
        self.convert_btn = QPushButton("Reclassify Selected Transaction")
        self.convert_btn.setObjectName("SecondaryButton")
        self.edit_savings_btn = QPushButton("Edit Savings Entry")
        self.edit_savings_btn.setObjectName("SecondaryButton")
        reclass_row.addWidget(self.reclass_type_combo)
        reclass_row.addWidget(self.reclass_category_input)
        reclass_row.addWidget(self.convert_btn)
        reclass_row.addWidget(self.edit_savings_btn)
        ledger_layout.addLayout(reclass_row)
        self.transaction_list.currentRowChanged.connect(self.update_reclass_ui)

        summary_card = QFrame()
        summary_card.setObjectName("Card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(12)
        summary_header = QLabel("Monthly Summary")
        summary_header.setObjectName("SectionTitle")
        summary_layout.addWidget(summary_header)

        self.summary_display = QPlainTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setMinimumHeight(180)
        self.summary_display.setPlaceholderText("Summaries will appear here once you start logging transactions.")
        summary_layout.addWidget(self.summary_display)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        self.export_btn = QPushButton("Export Monthly CSV")
        self.chart_btn = QPushButton("Show Savings Chart")
        self.expense_chart_btn = QPushButton("Show Expense Pie")
        self.export_btn.setObjectName("SecondaryButton")
        self.chart_btn.setObjectName("SecondaryButton")
        self.expense_chart_btn.setObjectName("SecondaryButton")
        actions_row.addWidget(self.export_btn)
        actions_row.addWidget(self.chart_btn)
        actions_row.addWidget(self.expense_chart_btn)
        summary_layout.addLayout(actions_row)

        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setChildrenCollapsible(False)
        left_splitter.setHandleWidth(6)
        left_splitter.addWidget(form_card)
        left_splitter.addWidget(budget_card)
        left_splitter.addWidget(converter_card)
        left_splitter.setSizes([280, 200, 200])

        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setChildrenCollapsible(False)
        right_splitter.setHandleWidth(6)
        right_splitter.addWidget(ledger_card)
        right_splitter.addWidget(summary_card)
        right_splitter.setSizes([360, 260])

        left_container = QWidget()
        left_container_layout = QVBoxLayout(left_container)
        left_container_layout.setContentsMargins(0, 0, 0, 0)
        left_container_layout.setSpacing(0)
        left_container_layout.addWidget(left_splitter)

        right_container = QWidget()
        right_container_layout = QVBoxLayout(right_container)
        right_container_layout.setContentsMargins(0, 0, 0, 0)
        right_container_layout.setSpacing(0)
        right_container_layout.addWidget(right_splitter)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        content_splitter.setHandleWidth(6)
        content_splitter.addWidget(left_container)
        content_splitter.addWidget(right_container)
        content_splitter.setSizes([520, 520])

        content_wrapper = QWidget()
        content_wrapper_layout = QVBoxLayout(content_wrapper)
        content_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        content_wrapper_layout.setSpacing(0)
        content_wrapper_layout.addWidget(content_splitter)

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(6)
        main_splitter.addWidget(header_wrapper)
        main_splitter.addWidget(content_wrapper)
        main_splitter.setSizes([180, 720])

        layout.addWidget(main_splitter)

        self.income_btn.clicked.connect(lambda: self.add_tx("income"))
        self.expense_btn.clicked.connect(lambda: self.add_tx("expense"))
        self.savings_btn.clicked.connect(lambda: self.add_tx("savings"))
        self.add_budget_btn.clicked.connect(self.add_budget)
        self.export_btn.clicked.connect(self.export_monthly_data)
        self.chart_btn.clicked.connect(self.show_savings_visual)
        self.expense_chart_btn.clicked.connect(self.show_expense_pie_chart)
        self.currency_convert_btn.clicked.connect(self.perform_currency_conversion)
        self.currency_update_btn.clicked.connect(self.refresh_exchange_rates)
        self.convert_btn.clicked.connect(self.reclassify_selected_transaction)
        self.edit_savings_btn.clicked.connect(self.edit_selected_savings)

        self.refresh_currency_options()
        self.apply_theme()
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()

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

    def _normalize_transaction(self, row: dict) -> dict:
        tx_id = row.get("tx_id", "").strip()
        ttype = (row.get("type", "expense") or "expense").lower()
        if ttype not in {"income", "expense", "savings"}:
            ttype = "expense"
        raw_amount = row.get("amount_rm", row.get("amount", "0"))
        try:
            amount = money(raw_amount)
        except Exception:
            amount = Decimal("0.00")
        category = row.get("category") or ("Savings" if ttype == "savings" else "General")
        category = category.strip() or ("Savings" if ttype == "savings" else "General")
        desc = (row.get("desc") or row.get("description") or "").strip()
        tx_date = (row.get("date") or "").strip()
        try:
            if tx_date:
                date.fromisoformat(tx_date)
            else:
                raise ValueError
        except ValueError:
            tx_date = date.today().isoformat()
        return {
            "tx_id": tx_id,
            "date": tx_date,
            "type": ttype,
            "category": category,
            "amount": amount,
            "desc": desc,
        }

    def load_ledger(self):
        self.transaction_list.clear()
        self.balance = Decimal("0.00")
        self.transactions = []
        self.categories = set()
        if not LEDGER_CSV.exists():
            return
        try:
            with LEDGER_CSV.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for raw in reader:
                    tx = self._normalize_transaction(raw)
                    self.transactions.append(tx)
                    if tx["category"]:
                        self.categories.add(tx["category"])
                    if tx["type"] == "income":
                        self.balance += tx["amount"]
                    else:
                        self.balance -= tx["amount"]
        except FileNotFoundError:
            return

        for tx in self.transactions:
            sign = "+" if tx["type"] == "income" else "-"
            tx_id = tx["tx_id"] or "-"
            display = f"{tx['date']} | {tx['category']} | {sign} RM{tx['amount']:.2f} | {tx['desc']}  ({tx_id})"
            self.transaction_list.addItem(display)

    def current_month_transactions(self, type_filter: str | None = None) -> list[dict]:
        today = date.today()
        matches: list[dict] = []
        for tx in self.transactions:
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year != today.year or tx_date.month != today.month:
                continue
            if type_filter and tx["type"] != type_filter:
                continue
            matches.append(tx)
        return matches

    def load_budgets(self):
        self.budget_list.clear()
        self.budget_map = {}
        if not BUDGET_CSV.exists():
            return
        try:
            with BUDGET_CSV.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = (row.get("category") or "").strip()
                    if not category:
                        continue
                    try:
                        amount = money(row.get("monthly_budget_rm", "0"))
                    except Exception:
                        continue
                    self.budget_map[category] = amount
        except FileNotFoundError:
            return

        today_spend = {cat: self.category_monthly_total(cat) for cat in self.budget_map}
        for category in sorted(self.budget_map.keys()):
            allowance = self.budget_map[category]
            spent = today_spend.get(category, Decimal("0.00"))
            self.budget_list.addItem(f"{category}: RM {spent:.2f} spent / RM {allowance:.2f} budget")

    def save_budgets(self):
        ensure_writable(BUDGET_CSV)
        with BUDGET_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(BUDGET_HEADER)
            for category in sorted(self.budget_map.keys()):
                writer.writerow([category, f"{self.budget_map[category]:.2f}"])
        ensure_private_file(BUDGET_CSV)

    def add_budget(self):
        category = self.budget_category_input.text().strip()
        if not category:
            QMessageBox.warning(self, "Missing", "Category name is required for a budget.")
            return
        amount_text = self.budget_amount_input.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Missing", "Budget amount is required.")
            return
        try:
            amount = money(amount_text)
            if amount < 0:
                raise ValueError
        except Exception:
            QMessageBox.critical(self, "Invalid", "Enter a valid budget amount, e.g. 250.00")
            return

        self.budget_map[category] = amount
        self.save_budgets()
        self.load_budgets()
        self.refresh_category_options()
        self.update_summary()
        self.budget_category_input.clear()
        self.budget_amount_input.clear()
        QMessageBox.information(self, "Budget saved", f"{category} budget set to RM {amount:.2f}.")

    def refresh_category_options(self):
        current_text = self.category_input.currentText().strip()
        categories = sorted(set(self.categories) | set(self.budget_map.keys()))
        self.category_input.blockSignals(True)
        self.category_input.clear()
        if categories:
            self.category_input.addItems(categories)
        if current_text:
            self.category_input.setEditText(current_text)
        else:
            self.category_input.setCurrentIndex(-1)
        self.category_input.blockSignals(False)
        self.refresh_currency_options()

    def refresh_currency_options(self):
        if not hasattr(self, "currency_target_combo"):
            return
        rates = self.exchange_rates or {}
        codes = sorted(code for code in rates.keys() if code != self.base_currency and code != 'ILS')
        if not codes:
            codes = [code for code in DEFAULT_TARGET_CURRENCIES if code != self.base_currency and code != 'ILS']
        display_pairs = []
        for code in codes:
            name = FALLBACK_NAMES.get(code, code)
            display_pairs.append((code, f"{code} - {name}"))
        self.currency_target_combo.blockSignals(True)
        current_index = self.currency_target_combo.currentIndex()
        current_code = self.currency_target_combo.itemData(current_index) if current_index >= 0 else None
        self.currency_target_combo.clear()
        matched_index = -1
        for index, (code, label) in enumerate(display_pairs):
            self.currency_target_combo.addItem(label, code)
            if code == current_code:
                matched_index = index
        self.currency_target_combo.blockSignals(False)
        if matched_index >= 0:
            self.currency_target_combo.setCurrentIndex(matched_index)
        elif self.currency_target_combo.count() > 0:
            self.currency_target_combo.setCurrentIndex(0)
        current_index = self.currency_target_combo.currentIndex()
        self.selected_currency_code = self.currency_target_combo.itemData(current_index) if current_index >= 0 else None
        line_edit = self.currency_target_combo.lineEdit()
        if line_edit is not None:
            line_edit.selectAll()
        self.update_rates_info_label()

    def update_rates_info_label(self):
        if not hasattr(self, "currency_info_label"):
            return
        if not self.rates_timestamp:
            self.currency_info_label.setText("Rates last updated: never. Refresh to download the latest public market rates.")
            return
        last_updated = time.strftime("%d %b %Y %H:%M", time.localtime(self.rates_timestamp))
        self.currency_info_label.setText(
            f"Rates last updated: {last_updated} (source: open.er-api.com)"
        )

    def perform_currency_conversion(self):
        if not hasattr(self, "currency_amount_input"):
            return
        amount_text = self.currency_amount_input.text().strip()
        if not amount_text:
            QMessageBox.information(self, "Missing amount", "Enter an amount in MYR to convert.")
            return
        try:
            amount = money(amount_text)
        except Exception:
            QMessageBox.critical(self, "Invalid amount", "Enter a valid numeric amount, e.g. 50.00")
            return
        current_index = self.currency_target_combo.currentIndex()
        if current_index < 0:
            QMessageBox.warning(self, "Choose currency", "Select a target currency.")
            return
        target_code = self.currency_target_combo.itemData(current_index)
        if not target_code:
            target_code = self.currency_target_combo.currentText().split(" - ")[0].strip()
        if not target_code:
            QMessageBox.warning(self, "Choose currency", "Select a target currency.")
            return
        rate = self.exchange_rates.get(target_code)
        if rate is None:
            if not self._update_exchange_rates(show_message=False):
                QMessageBox.warning(
                    self,
                    "Missing rate",
                    "Could not download exchange rates. Please try again later.",
                )
                return
            rate = self.exchange_rates.get(target_code)
            if rate is None:
                QMessageBox.warning(
                    self,
                    "Missing rate",
                    "That currency does not have a cached rate yet. Refresh rates first.",
                )
                return
        converted = money(amount * Decimal(str(rate)))
        self.currency_result_label.setText(
            f"Result: {self.base_currency} {amount:.2f} = {target_code} {converted:.2f}"
        )

    def refresh_exchange_rates(self):
        self._update_exchange_rates(show_message=True, force=True)

    def _update_exchange_rates(self, show_message: bool = True, force: bool = False) -> bool:
        now = int(time.time())
        if not force and self.rates_timestamp and now - self.rates_timestamp < RATES_TTL_SECONDS:
            if show_message:
                QMessageBox.information(
                    self,
                    "Rates up to date",
                    "Using cached exchange rates saved earlier in this session.",
                )
            return True
        if not hasattr(self, "currency_update_btn"):
            return False

        fetched = None
        try:
            response = requests.get(
                f"{RATES_API_URL}/{self.base_currency}",
                timeout=10,
            )
            response.raise_for_status()
            fetched = response.json()
        except Exception as exc:
            if show_message:
                QMessageBox.warning(
                    self,
                    "Using cached rates",
                    f"Could not download exchange rates right now. Retaining your previous rates.\nReason: {exc}",
                )
            return bool(self.exchange_rates)

        if fetched is None:
            return bool(self.exchange_rates)

        if fetched.get("result") != "success":
            message = fetched.get("error-type") or fetched.get("documentation") or "Unknown error."
            if show_message:
                QMessageBox.warning(
                    self,
                    "Using cached rates",
                    f"The rate service returned an error. Keeping cached rates.\nDetails: {message}",
                )
            return bool(self.exchange_rates)

        rates = fetched.get("rates") or fetched.get("conversion_rates")
        if not isinstance(rates, dict) or not rates:
            snippet = json.dumps(fetched, indent=2)[:400] if isinstance(fetched, dict) else str(fetched)[:400]
            if show_message:
                QMessageBox.warning(
                    self,
                    "Using cached rates",
                    f"Unexpected response from rate service. Keeping cached rates.\nPayload snippet:\n{snippet}",
                )
            return bool(self.exchange_rates)

        cleaned = {}
        for code, value in rates.items():
            try:
                cleaned[code] = float(value)
            except (TypeError, ValueError):
                continue
        cleaned[self.base_currency] = 1.0
        self.exchange_rates = cleaned
        self.rates_timestamp = int(fetched.get("time_last_update_unix") or time.time())
        store_rates(
            {
                "base": self.base_currency,
                "timestamp": self.rates_timestamp,
                "rates": self.exchange_rates,
            }
        )
        self.refresh_currency_options()
        self.currency_result_label.setText("Result: -")
        if show_message:
            QMessageBox.information(
                self,
                "Rates updated",
                "Latest exchange rates downloaded from open.er-api.com. No personal data was shared during this request.",
            )
        return True

    def update_summary(self):
        if not self.transactions:
            self.summary_display.setPlainText("No transactions recorded yet.")
            return

        today = date.today()
        totals = defaultdict(lambda: Decimal("0.00"))
        category_totals = defaultdict(lambda: Decimal("0.00"))

        for tx in self.transactions:
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year == today.year and tx_date.month == today.month:
                amount = tx["amount"]
                ttype = tx["type"]
                if ttype == "income":
                    totals["income"] += amount
                elif ttype == "savings":
                    totals["savings"] += amount
                    category_totals[tx["category"]] += amount
                else:
                    totals["expense"] += amount
                    category_totals[tx["category"]] += amount

        if not any(totals.values()) and not category_totals:
            self.summary_display.setPlainText("No transactions recorded yet for this month.")
            return

        net = totals["income"] - totals["expense"] - totals["savings"]
        lines = [
            f"Month: {today.strftime('%B %Y')}",
            f"Total Income: RM {totals['income']:.2f}",
            f"Total Spending: RM {totals['expense']:.2f}",
            f"Total Savings: RM {totals['savings']:.2f}",
            f"Net Position: RM {net:.2f}",
        ]

        if category_totals:
            lines.append("")
            lines.append("Category breakdown:")
            for category in sorted(category_totals.keys()):
                spent = category_totals[category]
                budget = self.budget_map.get(category)
                if budget:
                    variance = budget - spent
                    status = "within budget" if spent <= budget else "over budget"
                    lines.append(
                        f"- {category}: RM {spent:.2f} / RM {budget:.2f} "
                        f"({status}, variance RM {variance:.2f})"
                    )
                else:
                    lines.append(f"- {category}: RM {spent:.2f} (no budget set)")
        else:
            lines.append("")
            lines.append("No category spending recorded this month.")

        self.summary_display.setPlainText("\n".join(lines))

    def category_monthly_total(self, category: str) -> Decimal:
        today = date.today()
        total = Decimal("0.00")
        for tx in self.transactions:
            if tx["category"] != category:
                continue
            if tx["type"] not in {"expense", "savings"}:
                continue
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year == today.year and tx_date.month == today.month:
                total += tx["amount"]
        return total

    def update_reclass_ui(self, row: int):
        if not hasattr(self, "reclass_type_combo"):
            return
        if row < 0 or row >= len(self.transactions):
            self.reclass_type_combo.setCurrentIndex(0)
            self.reclass_category_input.clear()
            return
        tx = self.transactions[row]
        idx = self.reclass_type_combo.findText(tx["type"])
        if idx >= 0:
            self.reclass_type_combo.blockSignals(True)
            self.reclass_type_combo.setCurrentIndex(idx)
            self.reclass_type_combo.blockSignals(False)
        self.reclass_category_input.setText(tx["category"] or "")

    def edit_selected_savings(self):
        row = self.transaction_list.currentRow()
        if row < 0 or row >= len(self.transactions):
            QMessageBox.information(self, "Select a transaction", "Choose a savings transaction to edit.")
            return

        tx = self.transactions[row]
        if tx["type"] != "savings":
            QMessageBox.information(self, "Not a savings entry", "Only savings transactions can be edited with this action.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Savings Entry")
        layout = QVBoxLayout(dialog)

        amount_edit = QLineEdit(f"{tx['amount']:.2f}")
        amount_edit.setValidator(QDoubleValidator(0.01, 1_000_000.0, 2))
        layout.addWidget(QLabel("Amount (RM)"))
        layout.addWidget(amount_edit)

        desc_edit = QLineEdit(tx["desc"])
        layout.addWidget(QLabel("Description"))
        layout.addWidget(desc_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() != QDialog.Accepted:
            return

        amount_text = amount_edit.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Missing amount", "Enter an amount to continue.")
            return
        try:
            new_amount = money(amount_text)
            if new_amount <= 0:
                raise ValueError
        except Exception:
            QMessageBox.critical(self, "Invalid amount", "Enter a valid numeric amount, e.g. 50.00")
            return

        new_desc = desc_edit.text().strip() or "No description"

        if not self.update_transaction_record(tx["tx_id"], new_amount=new_amount, new_desc=new_desc):
            QMessageBox.critical(self, "Update failed", "Could not update the savings entry in the ledger.")
            return

        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        if 0 <= row < self.transaction_list.count():
            self.transaction_list.setCurrentRow(row)
        QMessageBox.information(self, "Savings updated", "Savings entry updated successfully.")


    def reclassify_selected_transaction(self):
        row = self.transaction_list.currentRow()
        if row < 0 or row >= len(self.transactions):
            QMessageBox.information(self, "Select a transaction", "Choose a transaction to reclassify.")
            return

        tx = self.transactions[row]
        if not tx["tx_id"]:
            QMessageBox.warning(
                self,
                "Cannot convert",
                "This transaction does not have an ID and cannot be converted in-place.",
            )
            return

        new_type = (self.reclass_type_combo.currentText() or "").strip().lower()
        if new_type not in {"income", "expense", "savings"}:
            QMessageBox.warning(self, "Choose a type", "Select a new transaction type from the dropdown.")
            return

        if new_type == "savings":
            default_category = tx["category"] if tx["category"] and tx["category"] != "General" else "Savings"
        elif new_type == "income":
            default_category = tx["category"] if tx["category"] and tx["category"] not in {"General", "Savings"} else "Income"
        else:
            default_category = tx["category"] or "General"

        category_input = self.reclass_category_input.text().strip()
        category = category_input or default_category

        if new_type == tx["type"] and category == tx["category"]:
            QMessageBox.information(self, "No changes", "This transaction already matches the requested type and category.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm reclassification",
            (
                f"Convert transaction {tx['tx_id']}?\n"
                f"Amount: RM {tx['amount']:.2f}\n"
                f"Original type: {tx['type']}\n"
                f"Original category: {tx['category'] or 'N/A'}\n"
                f"New type: {new_type}\n"
                f"New category: {category}"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        if not self.update_transaction_record(tx["tx_id"], new_type, category):
            QMessageBox.critical(self, "Update failed", "Could not update the transaction in the ledger file.")
            return

        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        if 0 <= row < self.transaction_list.count():
            self.transaction_list.setCurrentRow(row)
        self.reclass_category_input.clear()
        QMessageBox.information(self, "Updated", "Transaction has been updated.")

    def update_transaction_record(
        self,
        tx_id: str,
        new_type: str | None = None,
        new_category: str | None = None,
        new_amount: Decimal | None = None,
        new_desc: str | None = None,
    ) -> bool:
        if not tx_id:
            return False
        try:
            with LEDGER_CSV.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                header = reader.fieldnames or []
        except FileNotFoundError:
            return False

        updated = False
        for row in rows:
            if row.get("tx_id") == tx_id:
                if new_type is not None:
                    row["type"] = new_type
                if new_category is not None:
                    row["category"] = new_category
                if new_amount is not None:
                    row["amount_rm"] = f"{Decimal(new_amount):.2f}"
                if new_desc is not None:
                    row["desc"] = new_desc
                updated = True
                break
        if not updated:
            return False

        ensure_writable(LEDGER_CSV)
        fieldnames = []
        for key in header:
            if key and key not in fieldnames:
                fieldnames.append(key)
        for key in LEDGER_HEADER:
            if key not in fieldnames:
                fieldnames.append(key)

        with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "") for field in fieldnames})
        ensure_private_file(LEDGER_CSV)
        return True

    def export_monthly_data(self):
        monthly = self.current_month_transactions()
        if not monthly:
            QMessageBox.information(self, "Nothing to export", "No transactions recorded for the current month.")
            return
        default_name = f"student_budget_{date.today().strftime('%Y_%m')}.csv"
        suggested_path = Path.home() / default_name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Monthly Data",
            str(suggested_path),
            "CSV Files (*.csv)",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "type", "category", "amount_rm", "description", "tx_id"])
                for tx in monthly:
                    writer.writerow([
                        tx["date"],
                        tx["type"],
                        tx["category"],
                        f"{tx['amount']:.2f}",
                        tx["desc"],
                        tx["tx_id"],
                    ])
        except Exception as exc:
            QMessageBox.critical(self, "Export failed", f"Could not export data:\n{exc}")
            return
        QMessageBox.information(self, "Export complete", f"Monthly data exported to:\n{file_path}")

    def show_savings_visual(self):
        monthly_savings = self.current_month_transactions("savings")
        if not monthly_savings:
            QMessageBox.information(self, "No savings recorded", "Log some savings transactions to view the chart.")
            return
        if not MATPLOTLIB_AVAILABLE:
            QMessageBox.warning(
                self,
                "Visualization unavailable",
                "matplotlib is required to render charts.\nInstall it with: pip install matplotlib",
            )
            return
        if Figure is None or FigureCanvasQTAgg is None:
            QMessageBox.warning(
                self,
                "Visualization unavailable",
                "matplotlib could not be loaded in this environment.",
            )
            return
        totals = defaultdict(lambda: Decimal("0.00"))
        for tx in monthly_savings:
            totals[tx["category"]] += tx["amount"]
        categories = sorted(totals.keys())
        if not categories:
            QMessageBox.information(self, "No savings categories", "Savings entries need a category to build the chart.")
            return
        values = [float(totals[cat]) for cat in categories]

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        bars = ax.bar(categories, values, color="#03A9F4")
        ax.set_title(f"Monthly Savings ({date.today().strftime('%B %Y')})")
        ax.set_ylabel("Amount (RM)")
        ax.set_ylim(bottom=0)
        ax.tick_params(axis="x", labelrotation=20)
        for bar, val in zip(bars, values, strict=False):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"RM {val:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        fig.tight_layout()

        dialog = QDialog(self)
        dialog.setWindowTitle("Monthly Savings Visualization")
        dialog.resize(640, 420)
        layout = QVBoxLayout(dialog)
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)
        canvas.draw()
        dialog.exec_()

    def show_expense_pie_chart(self):
        monthly_expenses = self.current_month_transactions("expense")
        if not monthly_expenses:
            QMessageBox.information(self, "No expenses recorded", "Log some expenses to view the pie chart.")
            return
        if not MATPLOTLIB_AVAILABLE or Figure is None or FigureCanvasQTAgg is None:
            QMessageBox.warning(
                self,
                "Visualization unavailable",
                "matplotlib is required to render charts.\nInstall it with: pip install matplotlib",
            )
            return
        totals = defaultdict(lambda: Decimal("0.00"))
        for tx in monthly_expenses:
            category = tx["category"] or "General"
            totals[category] += tx["amount"]
        categories = [cat for cat, total in totals.items() if total > 0]
        if not categories:
            QMessageBox.information(self, "No expenses recorded", "No positive expenses available for this month.")
            return
        values = [float(totals[cat]) for cat in categories]
        total_sum = sum(values)
        if total_sum <= 0:
            QMessageBox.information(self, "No expenses recorded", "No positive expenses available for this month.")
            return

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        try:
            import matplotlib
            cmap = matplotlib.colormaps["viridis"]
            colors = [cmap(i / len(values)) for i in range(len(values))]
        except Exception:
            colors = None
        text_color = "#FFFFFF" if self.theme_mode == "dark" else "#212121"
        wedges, texts = ax.pie(
            values,
            labels=None,
            autopct=None,
            startangle=90,
            colors=colors,
            textprops={"color": text_color},
        )
        legend_labels = [f"{cat}: RM {val:.2f}" for cat, val in zip(categories, values, strict=False)]
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            facecolor="#2B2B34" if self.theme_mode == "dark" else "#F2F2F2",
            edgecolor="#3C3C45" if self.theme_mode == "dark" else "#D0D0D0",
        )
        for text in legend.get_texts():
            text.set_color(text_color)
        legend.get_title().set_color(text_color)
        ax.axis("equal")
        ax.set_title(f"Monthly Expenses ({date.today().strftime('%B %Y')})")
        fig.tight_layout()

        dialog = QDialog(self)
        dialog.setWindowTitle("Monthly Expenses Pie Chart")
        dialog.resize(640, 420)
        layout = QVBoxLayout(dialog)
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)
        canvas.draw()
        dialog.exec_()


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
        raw_category = self.category_input.currentText().strip()
        if not raw_category:
            raw_category = "Savings" if ttype == "savings" else "General"
        txid = next_tx_id()
        tx_date = date.today().isoformat()

        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([txid, tx_date, ttype, raw_category, f"{amt:.2f}", desc])
        ensure_private_file(LEDGER_CSV)

        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.clear_inputs()

        if ttype != "income":
            budget = self.budget_map.get(raw_category)
            if budget:
                spent = self.category_monthly_total(raw_category)
                if spent > budget:
                    over = spent - budget
                    QMessageBox.warning(
                        self,
                        "Budget exceeded",
                        f"You have exceeded the {raw_category} budget by RM {over:.2f} this month.",
                    )

    def update_balance(self):
        self.balance_label.setText(f"Net Position: RM {self.balance:.2f}")
        self.balance_label.setStyleSheet("color: #81C784;" if self.balance >= 0 else "color: #E57373;")

    def clear_inputs(self):
        self.amount_input.clear()
        self.desc_input.clear()
        line_edit = self.category_input.lineEdit()
        if line_edit is not None:
            line_edit.clear()
        self.category_input.setCurrentIndex(-1)
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

