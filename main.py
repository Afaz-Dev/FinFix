from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox,
    QComboBox, QPlainTextEdit, QFileDialog, QDialog
)
from PyQt5.QtGui import QColor, QFont, QDoubleValidator
from PyQt5.QtCore import Qt
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from datetime import date
import csv, os, shutil, sys, stat, importlib
from pathlib import Path

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

DARK_STYLESHEET = """
QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI'; }
QLineEdit { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QListWidget { background-color: #1C1C1C; border: 1px solid #333333; border-radius: 8px; }
QPushButton#themeButton { background-color: #323232; border: 1px solid #4A4A4A; border-radius: 8px; padding: 6px 12px; color: #E0E0E0; }
QPushButton#themeButton:hover { background-color: #3C3C3C; }
QPlainTextEdit { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
QComboBox { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; }
""".strip()

LIGHT_STYLESHEET = """
QWidget { background-color: #F5F5F5; color: #212121; font-family: 'Segoe UI'; }
QLineEdit { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QListWidget { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; }
QPushButton#themeButton { background-color: #E0E0E0; border: 1px solid #BDBDBD; border-radius: 8px; padding: 6px 12px; color: #212121; }
QPushButton#themeButton:hover { background-color: #D5D5D5; }
QPlainTextEdit { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
QComboBox { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; }
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

        layout = QVBoxLayout(self)

        title = QLabel("Student Budget Tracker")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.theme_btn = QPushButton("Switch to Light Mode")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        self.balance_label = QLabel("Balance: RM 0.00")
        self.balance_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.balance_label)

        layout.addSpacing(8)
        tx_header = QLabel("Log Transaction")
        tx_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(tx_header)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount (e.g., 50.00)")
        self.amount_input.setValidator(QDoubleValidator(0.01, 1_000_000.0, 2))
        layout.addWidget(self.amount_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Lunch, Books)")
        layout.addWidget(self.desc_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.category_input.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.category_input.setMinimumContentsLength(12)
        line_edit = self.category_input.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText("Category (e.g., Food, Books, Savings)")
        layout.addWidget(self.category_input)

        btn_layout = QHBoxLayout()
        self.income_btn = self.createGradientButton("Add Income", "#4CAF50", "#2E7D32")
        self.expense_btn = self.createGradientButton("Add Expense", "#E91E63", "#880E4F")
        self.savings_btn = self.createGradientButton("Log Savings", "#03A9F4", "#01579B")
        btn_layout.addWidget(self.income_btn)
        btn_layout.addWidget(self.expense_btn)
        btn_layout.addWidget(self.savings_btn)
        layout.addLayout(btn_layout)

        layout.addSpacing(8)
        ledger_header = QLabel("Transactions")
        ledger_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(ledger_header)

        self.transaction_list = QListWidget()
        layout.addWidget(self.transaction_list)

        layout.addSpacing(8)
        budget_header = QLabel("Monthly Budgets")
        budget_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(budget_header)

        self.budget_category_input = QLineEdit()
        self.budget_category_input.setPlaceholderText("Category name (e.g., Food)")
        self.budget_amount_input = QLineEdit()
        self.budget_amount_input.setPlaceholderText("Monthly budget (RM)")
        self.budget_amount_input.setValidator(QDoubleValidator(0.00, 1_000_000.0, 2))
        budget_form = QHBoxLayout()
        budget_form.addWidget(self.budget_category_input)
        budget_form.addWidget(self.budget_amount_input)
        self.add_budget_btn = QPushButton("Save Budget")
        budget_form.addWidget(self.add_budget_btn)
        layout.addLayout(budget_form)

        self.budget_list = QListWidget()
        layout.addWidget(self.budget_list)

        layout.addSpacing(8)
        summary_header = QLabel("Monthly Summary")
        summary_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(summary_header)

        self.summary_display = QPlainTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setMinimumHeight(150)
        self.summary_display.setPlaceholderText("Summaries will appear here once you start logging transactions.")
        layout.addWidget(self.summary_display)

        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Monthly CSV")
        self.chart_btn = QPushButton("Show Savings Chart")
        export_layout.addWidget(self.export_btn)
        export_layout.addWidget(self.chart_btn)
        layout.addLayout(export_layout)

        # Connect actions
        self.income_btn.clicked.connect(lambda: self.add_tx("income"))
        self.expense_btn.clicked.connect(lambda: self.add_tx("expense"))
        self.savings_btn.clicked.connect(lambda: self.add_tx("savings"))
        self.add_budget_btn.clicked.connect(self.add_budget)
        self.export_btn.clicked.connect(self.export_monthly_data)
        self.chart_btn.clicked.connect(self.show_savings_visual)

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
