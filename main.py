from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMessageBox,
    QComboBox, QPlainTextEdit, QFileDialog, QDialog, QFrame, QDialogButtonBox,
    QWhatsThis, QSizePolicy, QScrollArea, QMainWindow, QMenuBar, QMenu, QAction, QStatusBar,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QProgressBar, QHeaderView, QShortcut,
    QGridLayout, QCheckBox, QFormLayout, QInputDialog, QGraphicsOpacityEffect
)
from PyQt5.QtGui import (
    QColor,
    QFont,
    QDoubleValidator,
    QHelpEvent,
    QKeySequence,
    QPainter,
    QDrag,
    QMouseEvent,
    QShowEvent,
    QCloseEvent,
    QResizeEvent,
    QMoveEvent,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
)
from PyQt5.QtCore import (
    Qt,
    QEvent,
    QPoint,
    QByteArray,
    QMimeData,
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    QTimer,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QSize,
    QAbstractAnimation,
    QObject,
    QRect,
    QVariantAnimation,
)
from PyQt5.QtPrintSupport import QPrinter
from typing import Dict, Optional, cast
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from datetime import date, timedelta
import csv, os, shutil, sys, stat, importlib, json, time, ctypes, calendar
from pathlib import Path

import requests
import sys

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

# App logo helpers (generated or assets/logo.png if available)
from app_logo import get_app_icon, get_logo_pixmap

# ============================================================================
# ANIMATION SYSTEM - Smooth Tweening Animations
# ============================================================================
# TweenButton:       Smooth position + shadow blur tweening on hover/press
# TweenListWidget:   Smooth scale tweening on list item hover
# Card Entrance:     Smooth slide-in (left to right) + fade tween on startup
# Input Focus:       CSS-based transitions for border & shadow
# 
# All animations use OutCubic easing for natural motion
# ============================================================================

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
RATES_TTL_SECONDS = 12 * 60 * 60             # reuse rates for half a day to limit network calls
RATES_API_URL = "https://open.er-api.com/v6/latest"
DEFAULT_TARGET_CURRENCIES = ["USD", "EUR", "GBP", "SGD", "AUD", "JPY", "CNY", "THB", "IDR", "TWD", "HKD", "VND"]
FALLBACK_RATES = {
    "MYR": 1.0,
    "USD": 0.24,
    "EUR": 0.19,
    "GBP": 0.16,
    "SGD": 0.28,
    "AUD": 0.32,
    "JPY": 32.0,
    "CNY": 1.52,
    "THB": 7.4,
    "IDR": 3600.0,
    "TWD": 7.3,
    "HKD": 1.88,
    "VND": 5700.0,
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
    "TWD": "New Taiwan Dollar",
    "VND": "Vietnamese Dong",
}

DARK_STYLESHEET = """
QWidget { background-color: #121212; color: #E0E0E0; font-family: 'Segoe UI'; }
QLineEdit { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; transition: all 0.2s; }
QLineEdit:focus { border: 2px solid #6366f1; box-shadow: 0 0 12px rgba(99, 102, 241, 0.3); }
QListWidget { background-color: #1C1C1C; border: 1px solid #333333; border-radius: 8px; font-family: 'Consolas', 'Cascadia Mono', monospace; }
QListWidget::item { padding: 6px 8px; border-bottom: 1px solid #2C2C34; transition: all 0.15s; }
QListWidget::item:hover { background-color: #252530; }
QListWidget::item:alternate { background-color: #1F1F26; }
QListWidget::item:last { border-bottom: none; }
QListWidget::item:selected { background-color: #314261; color: #FFFFFF; }
QListWidget::item:selected:!active { background-color: #2C3B58; color: #FFFFFF; }
QPushButton#themeButton { background-color: #323232; border: 1px solid #4A4A4A; border-radius: 8px; padding: 6px 12px; color: #E0E0E0; transition: all 0.2s ease-out; }
QPushButton#themeButton:hover { background-color: #3C3C3C; border: 1px solid #6366f1; }
QPushButton#themeButton:pressed { transform: scale(0.98); }
QPlainTextEdit { background-color: #1E1E1E; border: 1px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; transition: all 0.2s; }
QPlainTextEdit:focus { border: 1px solid #6366f1; }
QComboBox { background-color: #1E1E1E; border: 2px solid #333333; border-radius: 8px; padding: 6px; color: #E0E0E0; transition: all 0.2s; }
QComboBox:focus { border: 2px solid #6366f1; }
QComboBox:hover { border: 2px solid #4A4A6A; }
QFrame#HeaderBar { background-color: #1D1D28; border-radius: 18px; }
QLabel#Title { font-size: 18px; font-weight: 600; background-color: transparent; }
QLabel#Subtitle { color: #B0BEC5; font-size: 12px; background-color: transparent; }
QLabel#BalanceValue { background-color: #1E3A29; border-radius: 14px; padding: 8px 14px; font-size: 14px; font-weight: 600; color: #A5D6A7; transition: all 0.3s; }
QFrame#Card { background-color: #1A1A1F; border: 1px solid #2C2C34; border-radius: 16px; transition: all 0.3s; }
QFrame#Card:hover { border: 1px solid #404050; }
QFrame#ActionBar { background-color: #16161C; border: 1px solid #2C2C34; border-radius: 12px; }
QFrame#SummaryBubble { background-color: #1C1C21; border: 1px solid #2C2C34; border-radius: 14px; }
QLabel#SummaryText { color: #E0E0E0; font-size: 12px; background-color: transparent; }
QLabel#SummaryCaption { color: #CFD8DC; font-size: 12px; background-color: transparent; }
QLabel#SectionTitle { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #9FA8DA; background-color: transparent; }
QFrame#SummaryKPI { background-color: #24242E; border: 1px solid #343447; border-radius: 12px; transition: all 0.2s; }
QFrame#SummaryKPI:hover { border: 1px solid #4A4A60; }
QLabel#SummaryKPIHeader { font-size: 12px; font-weight: 600; color: #9FA8DA; }
QLabel#SummaryKPIValue { font-size: 18px; font-weight: 700; color: #FFFFFF; }
QLabel#SummaryKPIDelta { font-size: 12px; color: #B0BEC5; }
QFrame#SummarySubCard { background-color: #1F1F26; border: 1px solid #2E2E38; border-radius: 12px; transition: all 0.2s; }
QFrame#SummarySubCard:hover { border: 1px solid #404050; }
QTableWidget#SummaryTable { background-color: #1E1E24; border: 1px solid #2C2C34; border-radius: 10px; gridline-color: #2C2C34; }
QTableWidget#SummaryTable::item { padding: 6px; font-size: 12px; background-color: #1E1E24; color: #E0E0E0; transition: all 0.15s; }
QTableWidget#SummaryTable::item:hover { background-color: #262631; }
QTableWidget#SummaryTable::item:alternate { background-color: #262631; }
QTableWidget#SummaryTable::item:selected { background-color: #2F3B59; color: #FFFFFF; }
QTableWidget#SummaryTable QHeaderView::section { background-color: #252532; color: #E0E0E0; font-size: 12px; padding: 6px; border: none; }
QListWidget#SummaryAlerts { background-color: #1E1E24; border: 1px solid #2C2C34; border-radius: 10px; padding: 6px; font-family: 'Segoe UI'; }
QListWidget#SummaryAlerts::item { border-bottom: 1px solid #2C2C34; padding: 6px 4px; transition: all 0.15s; }
QListWidget#SummaryAlerts::item:hover { background-color: #252530; }
QListWidget#SummaryAlerts::item:last { border-bottom: none; }
QPushButton#SecondaryButton { background-color: #2A2A33; border: 1px solid #3A3A45; border-radius: 10px; padding: 9px 12px; font-weight: 600; color: #F5F5F5; transition: all 0.2s ease-out; }
QPushButton#SecondaryButton:hover { background-color: #353543; border: 1px solid #4A5A6A; transform: translateY(-2px); }
QPushButton#SecondaryButton:pressed { transform: translateY(0px); }
QLabel#InfoText { color: #B0BEC5; font-size: 11px; background-color: transparent; }
""".strip()

LIGHT_STYLESHEET = """
QWidget { background-color: #F5F5F5; color: #212121; font-family: 'Segoe UI'; }
QLineEdit { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; transition: all 0.2s; }
QLineEdit:focus { border: 2px solid #6366f1; box-shadow: 0 0 12px rgba(99, 102, 241, 0.2); }
QListWidget { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; font-family: 'Consolas', 'Cascadia Mono', monospace; }
QListWidget::item { padding: 6px 8px; border-bottom: 1px solid #E0E0E0; transition: all 0.15s; }
QListWidget::item:hover { background-color: #F0F3FF; }
QListWidget::item:alternate { background-color: #F4F7FF; }
QListWidget::item:selected { background-color: #CCE0FF; color: #102A43; }
QListWidget::item:selected:!active { background-color: #D7E6FF; color: #102A43; }
QListWidget::item:last { border-bottom: none; }
QPushButton#themeButton { background-color: #E0E0E0; border: 1px solid #BDBDBD; border-radius: 8px; padding: 6px 12px; color: #212121; transition: all 0.2s ease-out; }
QPushButton#themeButton:hover { background-color: #D5D5D5; border: 1px solid #6366f1; }
QPushButton#themeButton:pressed { transform: scale(0.98); }
QPlainTextEdit { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; transition: all 0.2s; }
QPlainTextEdit:focus { border: 1px solid #6366f1; }
QComboBox { background-color: #FFFFFF; border: 2px solid #D0D0D0; border-radius: 8px; padding: 6px; color: #212121; transition: all 0.2s; }
QComboBox:focus { border: 2px solid #6366f1; }
QComboBox:hover { border: 2px solid #B0B0D0; }
QFrame#HeaderBar { background-color: #FFFFFF; border-radius: 18px; border: 1px solid #E0E0E0; transition: all 0.2s; }
QFrame#HeaderBar:hover { border: 1px solid #D0D0D0; }
QLabel#Title { font-size: 18px; font-weight: 600; color: #1B5E20; background-color: transparent; }
QLabel#Subtitle { color: #5F6368; font-size: 12px; background-color: transparent; }
QLabel#BalanceValue { background-color: #E8F5E9; border-radius: 14px; padding: 8px 14px; font-size: 14px; font-weight: 600; color: #2E7D32; transition: all 0.3s; }
QFrame#Card { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 16px; transition: all 0.3s; }
QFrame#Card:hover { border: 1px solid #D0D0D0; }
QFrame#ActionBar { background-color: rgba(255, 255, 255, 0.85); border: 1px solid #DADADA; border-radius: 12px; }
QFrame#SummaryBubble { background-color: #F9F9F9; border: 1px solid #D6D6D6; border-radius: 14px; }
QLabel#SummaryText { color: #212121; font-size: 12px; background-color: transparent; }
QLabel#SummaryCaption { color: #455A64; font-size: 12px; background-color: transparent; }
QLabel#SectionTitle { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: #3949AB; background-color: transparent; }
QFrame#SummaryKPI { background-color: #FFFFFF; border: 1px solid #DADFE6; border-radius: 12px; transition: all 0.2s; }
QFrame#SummaryKPI:hover { border: 1px solid #C0CADB; }
QLabel#SummaryKPIHeader { font-size: 12px; font-weight: 600; color: #5F6368; }
QLabel#SummaryKPIValue { font-size: 18px; font-weight: 700; color: #1B5E20; }
QLabel#SummaryKPIDelta { font-size: 12px; color: #546E7A; }
QFrame#SummarySubCard { background-color: #FFFFFF; border: 1px solid #DADFE6; border-radius: 12px; transition: all 0.2s; }
QFrame#SummarySubCard:hover { border: 1px solid #C0CADB; }
QTableWidget#SummaryTable { background-color: #FFFFFF; border: 1px solid #D6D6D6; border-radius: 10px; gridline-color: #E0E0E0; }
QTableWidget#SummaryTable::item { padding: 6px; font-size: 12px; background-color: #FFFFFF; color: #212121; transition: all 0.15s; }
QTableWidget#SummaryTable::item:hover { background-color: #F8FAFE; }
QTableWidget#SummaryTable::item:alternate { background-color: #F4F6FB; }
QTableWidget#SummaryTable::item:selected { background-color: #D9E4FF; color: #1A237E; }
QTableWidget#SummaryTable QHeaderView::section { background-color: #ECEFF1; color: #37474F; font-size: 12px; padding: 6px; border: none; }
QListWidget#SummaryAlerts { background-color: #FFFFFF; border: 1px solid #D6D6D6; border-radius: 10px; padding: 6px; font-family: 'Segoe UI'; }
QListWidget#SummaryAlerts::item { border-bottom: 1px solid #E0E0E0; padding: 6px 4px; transition: all 0.15s; }
QListWidget#SummaryAlerts::item:hover { background-color: #F8FAFE; }
QListWidget#SummaryAlerts::item:last { border-bottom: none; }
QPushButton#SecondaryButton { background-color: #F0F0F0; border: 1px solid #D0D0D0; border-radius: 10px; padding: 9px 12px; font-weight: 600; color: #1F1F1F; transition: all 0.2s ease-out; }
QPushButton#SecondaryButton:hover { background-color: #E4E4E4; border: 1px solid #6366f1; transform: translateY(-2px); }
QPushButton#SecondaryButton:pressed { transform: translateY(0px); }
QLabel#InfoText { color: #5F6368; font-size: 11px; background-color: transparent; }
""".strip()


class TweenButton(QPushButton):
    """Button with smooth scale/position tweening animations on hover/press."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._anim: Optional[QAbstractAnimation] = None
        self._shadow = QGraphicsDropShadowEffect()
        self._shadow.setBlurRadius(12)
        self._shadow.setColor(QColor(0, 0, 0, 140))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._orig_geometry: Optional[QRect] = None
    
    def showEvent(self, a0: QShowEvent) -> None:
        event = a0
        super().showEvent(event)
        self._orig_geometry = self.geometry()
    
    def enterEvent(self, a0: QEvent) -> None:
        event = a0
        super().enterEvent(event)
        if self._anim and self._anim.state() == QAbstractAnimation.State.Running:
            self._anim.stop()
        
        # Tween shadow blur
        self._anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(12)
        self._anim.setEndValue(24)
        
        # Tween position (lift up)
        pos_anim = QPropertyAnimation(self, b"geometry")
        pos_anim.setDuration(200)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        pos_anim.setStartValue(self.geometry())
        
        if self._orig_geometry is not None:
            lifted = self._orig_geometry.translated(0, -4)
            pos_anim.setEndValue(lifted)
        
        group = QParallelAnimationGroup()
        group.addAnimation(self._anim)
        group.addAnimation(pos_anim)
        self._anim = group
        self._anim.start()
    
    def leaveEvent(self, a0: QEvent) -> None:
        event = a0
        super().leaveEvent(event)
        if self._anim and self._anim.state() == QAbstractAnimation.State.Running:
            self._anim.stop()
        
        self._anim = QPropertyAnimation(self._shadow, b"blurRadius")
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(24)
        self._anim.setEndValue(12)
        
        pos_anim = QPropertyAnimation(self, b"geometry")
        pos_anim.setDuration(150)
        pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        if self._orig_geometry is not None:
            pos_anim.setStartValue(self.geometry())
            pos_anim.setEndValue(self._orig_geometry)
        
        group = QParallelAnimationGroup()
        group.addAnimation(self._anim)
        group.addAnimation(pos_anim)
        self._anim = group
        self._anim.start()
    
    def mousePressEvent(self, e: QMouseEvent) -> None:
        event = e
        if self._anim and self._anim.state() == QAbstractAnimation.State.Running:
            self._anim.stop()
        
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(100)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(self.geometry())
        
        if self._orig_geometry is not None:
            pressed = self._orig_geometry.translated(1, 2)
            self._anim.setEndValue(pressed)
        
        self._anim.start()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        event = e
        if self._anim and self._anim.state() == QAbstractAnimation.State.Running:
            self._anim.stop()
        
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(100)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(self.geometry())
        
        if self._orig_geometry is not None and self.underMouse():
            lifted = self._orig_geometry.translated(0, -4)
            self._anim.setEndValue(lifted)
        elif self._orig_geometry is not None:
            self._anim.setEndValue(self._orig_geometry)
        
        self._anim.start()
        super().mouseReleaseEvent(event)



class TweenListWidget(QListWidget):
    """List widget with smooth scale tweening on item hover."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._item_anims: Dict[int, QVariantAnimation] = {}  # Track animations per item
        self.setMouseTracking(True)
    
    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        event = e
        super().mouseMoveEvent(event)
        item = self.itemAt(event.pos())
        
        # Reset all items first
        for idx in range(self.count()):
            self._tween_item_size(idx, 1.0, 150)
        
        # Tween hovered item
        if item:
            idx = self.row(item)
            self._tween_item_size(idx, 1.06, 200)
    
    def leaveEvent(self, a0: QEvent) -> None:
        event = a0
        super().leaveEvent(event)
        for idx in range(self.count()):
            self._tween_item_size(idx, 1.0, 150)
    
    def _tween_item_size(self, row: int, scale: float, duration: int) -> None:
        """Smooth scale tween for list item."""
        if row < 0 or row >= self.count():
            return

        item = self.item(row)
        if not item:
            return

        base_height = 30
        target_height = int(base_height * scale)
        current_height = item.sizeHint().height()

        anim = QVariantAnimation(self)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.setStartValue(current_height)
        anim.setEndValue(target_height)

        def apply_value(value: object, *, _item=item) -> None:
            if isinstance(value, (int, float)):
                height = int(value)
            elif hasattr(value, "__int__"):
                height = int(value)  # type: ignore[arg-type]
            else:
                return
            current_size = _item.sizeHint()
            _item.setSizeHint(QSize(current_size.width(), height))

        anim.valueChanged.connect(apply_value)

        old_anim = self._item_anims.get(row)
        if old_anim and old_anim.state() == QAbstractAnimation.State.Running:
            old_anim.stop()

        self._item_anims[row] = anim
        anim.start()

    """Helper class to fade in widgets smoothly."""
    
    @staticmethod
    def fade_in_widget(widget: QWidget, duration: int = 300):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()
        return anim


class FloatingConverterWindow(QWidget):
    closed = pyqtSignal()

    def closeEvent(self, a0: QCloseEvent) -> None:
        event = a0
        self.closed.emit()
        event.ignore()
        self.hide()

class CardWorkspace(QWidget):
    def __init__(self, columns: int = 2, parent: QWidget | None = None):
        super().__init__(parent)
        self.columns = max(1, columns)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(16)
        self._layout.setVerticalSpacing(16)
        for col in range(self.columns):
            self._layout.setColumnStretch(col, 1)
        self._cards: list[QWidget] = []
        self._handles: dict[QWidget, QWidget] = {}
        self._drag_start: QPoint | None = None
        self.setAcceptDrops(True)

    def add_card(self, card: QWidget, handle: QWidget) -> None:
        self._cards.append(card)
        self._handles[handle] = card
        handle.installEventFilter(self)
        handle.setCursor(Qt.CursorShape.OpenHandCursor)
        self._layout.addWidget(card, 0, 0)
        self._rebuild()

    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        obj = a0
        event = a1
        if not isinstance(obj, QWidget):
            return super().eventFilter(obj, event)
        card = self._handles.get(obj)
        if card is None:
            return super().eventFilter(obj, event)
        handle_widget = cast(QWidget, obj)

        def as_mouse_event(evt: QEvent) -> Optional[QMouseEvent]:
            return evt if isinstance(evt, QMouseEvent) else None

        if event.type() == QEvent.Type.MouseButtonPress:
            mouse_event = as_mouse_event(event)
            if mouse_event and mouse_event.button() == Qt.MouseButton.LeftButton:
                self._drag_start = mouse_event.globalPos()
                handle_widget.setCursor(Qt.CursorShape.ClosedHandCursor)
                return True
        elif event.type() == QEvent.Type.MouseMove:
            mouse_event = as_mouse_event(event)
            if (
                mouse_event is not None
                and bool(mouse_event.buttons() & Qt.MouseButton.LeftButton)
                and self._drag_start is not None
            ):
                if (
                    mouse_event.globalPos() - self._drag_start
                ).manhattanLength() >= QApplication.startDragDistance():
                    drag = QDrag(handle_widget)
                    mime = QMimeData()
                    mime.setData("application/x-card-id", QByteArray(str(id(card)).encode("ascii")))
                    drag.setMimeData(mime)
                    pixmap = card.grab()
                    drag.setPixmap(pixmap)
                    hot_spot = handle_widget.mapTo(card, mouse_event.pos())
                    drag.setHotSpot(hot_spot)
                    drag.exec_(Qt.DropAction.MoveAction)
                    handle_widget.setCursor(Qt.CursorShape.OpenHandCursor)
                    self._drag_start = None
                    return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            mouse_event = as_mouse_event(event)
            if mouse_event:
                handle_widget.setCursor(Qt.CursorShape.OpenHandCursor)
                self._drag_start = None
                return True
        return super().eventFilter(obj, event)

    def _mime_has_card_id(self, mime: Optional[QMimeData]) -> bool:
        return bool(mime and mime.hasFormat("application/x-card-id"))

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        event = a0
        mime = event.mimeData()
        if self._mime_has_card_id(mime):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, a0: QDragMoveEvent) -> None:
        event = a0
        mime = event.mimeData()
        if self._mime_has_card_id(mime):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, a0: QDropEvent) -> None:
        event = a0
        mime = event.mimeData()
        if not self._mime_has_card_id(mime):
            event.ignore()
            return
        assert mime is not None
        card_id_bytes = bytes(mime.data("application/x-card-id"))
        try:
            card_id = int(card_id_bytes.decode("ascii"))
        except ValueError:
            event.ignore()
            return
        card = next((c for c in self._cards if id(c) == card_id), None)
        if card is None:
            event.ignore()
            return
        pos = event.pos()
        reordered = [c for c in self._cards if c is not card]
        insert_at = self._index_for_position(pos, reordered)
        reordered.insert(insert_at, card)
        self._cards = reordered
        self._rebuild()
        event.acceptProposedAction()

    def _index_for_position(self, pos: QPoint, ordered: list[QWidget]) -> int:
        if not ordered:
            return 0
        for idx, widget in enumerate(ordered):
            if widget.isHidden():
                continue
            geom = widget.geometry()
            if pos.y() < geom.top():
                return idx
            if geom.contains(pos):
                return idx if pos.x() <= geom.center().x() else min(idx + 1, len(ordered))
            if pos.y() <= geom.bottom():
                return idx if pos.x() <= geom.center().x() else min(idx + 1, len(ordered))
        return len(ordered)

    def relayout(self) -> None:
        self._rebuild()

    def _rebuild(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(self)
        visible_cards = [card for card in self._cards if not card.isHidden()]
        for idx, card in enumerate(visible_cards):
            row = idx // self.columns
            col = idx % self.columns
            self._layout.addWidget(card, row, col)
        for col in range(self.columns):
            self._layout.setColumnStretch(col, 1)
        self._layout.invalidate()
        self.updateGeometry()

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

WINDOW_CONTEXT_HELP_HINT = getattr(Qt, "WindowContextHelpButtonHint", None)
HELP_EVENT_TYPES = {
    t
    for t in (
        getattr(QEvent, "ContextHelp", None),
        getattr(QEvent.Type, "ContextHelp", None),
        getattr(QEvent, "HelpRequest", None),
        getattr(QEvent.Type, "HelpRequest", None),
    )
    if t is not None
}


class HelpAwareDialog(QDialog):
    """QDialog that shows a help message when the title bar help button is pressed."""

    def __init__(self, parent=None, help_title: str = "Help", help_text: str = ""):
        super().__init__(parent)
        self._help_title = help_title or "Help"
        self._help_text = help_text.strip() or "No additional information is available."
        if WINDOW_CONTEXT_HELP_HINT is not None:
            self.setWindowFlag(WINDOW_CONTEXT_HELP_HINT, True)

    def event(self, a0: QEvent) -> bool:
        event = a0
        event_type = event.type()
        enter_mode_type = next(
            (
                t
                for t in (
                    getattr(QEvent, "EnterWhatsThisMode", None),
                    getattr(QEvent.Type, "EnterWhatsThisMode", None),
                )
                if t is not None
            ),
            None,
        )
        if enter_mode_type is not None and event_type == enter_mode_type:
            QMessageBox.information(self, self._help_title, self._help_text)
            QWhatsThis.leaveWhatsThisMode()
            return True
        if isinstance(event, QHelpEvent) or (HELP_EVENT_TYPES and event_type in HELP_EVENT_TYPES):
            QMessageBox.information(self, self._help_title, self._help_text)
            QWhatsThis.leaveWhatsThisMode()
            return True
        return super().event(event)


class ChartWindow(QMainWindow):
    """Standalone window that hosts a chart canvas with optional helper text."""

    def __init__(self, title: str, help_text: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        # Set window icon for chart windows
        try:
            self.setWindowIcon(get_app_icon())
        except Exception:
            pass
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setMinimumSize(520, 380)
        self.resize(720, 520)
        self._canvas_widget: QWidget | None = None
        self._help_label: QLabel | None = None
        self._help_text = ""
        self._theme_mode = "dark"

        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        self._layout = layout
        self.set_help_text(help_text)

    def set_canvas(self, canvas: QWidget) -> None:
        if self._canvas_widget is not None:
            old_canvas = self._canvas_widget
            self._layout.removeWidget(old_canvas)
            old_canvas.setParent(None)
            figure_obj = getattr(old_canvas, "figure", None)
            if callable(figure_obj):
                figure_obj = figure_obj()
            if figure_obj is not None:
                clear_method = getattr(figure_obj, "clear", None)
                if callable(clear_method):
                    try:
                        clear_method()
                    except Exception:
                        pass
            old_canvas.deleteLater()
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._layout.insertWidget(0, canvas)
        self._canvas_widget = canvas

    def set_help_text(self, help_text: str) -> None:
        help_text = (help_text or "").strip()
        if not help_text:
            if self._help_label is not None:
                self._layout.removeWidget(self._help_label)
                self._help_label.deleteLater()
                self._help_label = None
            self._help_text = ""
            return
        self._help_text = help_text
        if self._help_label is None:
            label = QLabel(help_text, self)
            label.setWordWrap(True)
            label.setObjectName("ChartHelpLabel")
            label.setContentsMargins(0, 8, 0, 0)
            self._layout.addWidget(label)
            self._help_label = label
        else:
            self._help_label.setText(help_text)
        self.apply_theme(self._theme_mode)

    def apply_theme(self, theme_mode: str) -> None:
        self._theme_mode = theme_mode
        if self._help_label is not None:
            help_color = "#B0BEC5" if theme_mode == "dark" else "#455A64"
            self._help_label.setStyleSheet(
                f"color: {help_color}; font-size: 11px; margin-top: 2px;"
            )


class BudgetTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FinFix : Student Budget Tracker")
        # Set main window icon
        try:
            self.setWindowIcon(get_app_icon())
        except Exception:
            pass
        self.setGeometry(200, 200, 520, 720)
        self.theme_mode = "dark"
        self.transactions = []
        self.categories = set()
        self.budget_map = {}
        self.balance = Decimal("0.00")
        self.undo_stack = []
        self.last_tx_type = "expense"
        self.show_converter = False
        self.toggle_converter_action: QAction | None = None
        self.converter_window: FloatingConverterWindow | None = None
        self.chart_windows: dict[str, ChartWindow] = {}
        ensure_storage()
        rate_snapshot = load_cached_rates()
        self.exchange_rates = rate_snapshot.get("rates", {"MYR": 1.0})
        self.base_currency = rate_snapshot.get("base", "MYR")
        self.rates_timestamp = rate_snapshot.get("timestamp", 0)
        self.selected_currency_code = None

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        self._build_menu()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to FinFix", 4000)
        self._install_shortcuts()

        header = QFrame()
        header.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)
        header_layout.setSpacing(18)

        # App logo on the left side of header
        try:
            logo_label = QLabel()
            logo_label.setObjectName("AppLogo")
            logo_pm = get_logo_pixmap(40)
            logo_label.setPixmap(logo_pm)
            logo_label.setFixedSize(40, 40)
            logo_label.setScaledContents(True)
            logo_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            header_layout.addWidget(logo_label)
        except Exception:
            pass

        title_container = QVBoxLayout()
        title_container.setSpacing(4)
        raw_user = os.getenv("USERNAME") or os.getenv("USER")
        welcome_text = f"Welcome, {raw_user}!" if raw_user else "Welcome!"
        welcome_label = QLabel(welcome_text)
        welcome_label.setObjectName("Subtitle")
        title_label = QLabel("FinFix : Student Budget Tracker")
        title_label.setObjectName("Title")
        subtitle = QLabel("Track spending, budgets, and savings with a clear monthly view.")
        subtitle.setObjectName("Subtitle")
        title_container.addWidget(welcome_label)
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

        header_actions.addWidget(self.balance_label)
        header_actions.addStretch(1)

        header_layout.addLayout(header_actions)

        header_wrapper = QWidget()
        header_wrapper_layout = QVBoxLayout(header_wrapper)
        header_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        header_wrapper_layout.setSpacing(0)
        header_wrapper_layout.addWidget(header)
        margins = header_layout.contentsMargins()
        balance_height = self.balance_label.sizeHint().height()
        stack_height = balance_height
        header_height = max(
            header.sizeHint().height(),
            stack_height + margins.top() + margins.bottom() + 4,
            110,
        )
        header_wrapper.setFixedHeight(header_height)
        header_wrapper.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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
        self.amount_input.returnPressed.connect(self.submit_default_transaction)
        form_layout.addWidget(self.amount_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description (e.g., Lunch, Books)")
        self.desc_input.returnPressed.connect(self.submit_default_transaction)
        form_layout.addWidget(self.desc_input)

        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.category_input.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.category_input.setMinimumContentsLength(12)
        line_edit = self.category_input.lineEdit()
        if line_edit is not None:
            line_edit.setPlaceholderText("Category (e.g., Food, Books, Savings)")
            line_edit.returnPressed.connect(self.submit_default_transaction)
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
        self.budget_list.setSpacing(6)
        self.budget_list.itemDoubleClicked.connect(self.edit_budget_item)
        budget_layout.addWidget(self.budget_list)

        self._build_converter_window()

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
        self.transaction_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.transaction_list.customContextMenuRequested.connect(self.open_transaction_context_menu)
        self.transaction_list.setSpacing(4)
        self.transaction_list.setUniformItemSizes(True)
        self.transaction_list.setAlternatingRowColors(True)
        ledger_layout.addWidget(self.transaction_list)

        self.use_savings_btn = QPushButton("Use Savings")
        self.use_savings_btn.setObjectName("SecondaryButton")
        self.edit_transaction_btn = QPushButton("Edit Transaction")
        self.edit_transaction_btn.setObjectName("SecondaryButton")
        self.delete_btn = QPushButton("Delete Transaction")
        self.delete_btn.setObjectName("SecondaryButton")
        action_bar = QFrame()
        action_bar.setObjectName("ActionBar")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(14, 10, 14, 10)
        action_layout.setSpacing(12)
        action_layout.addStretch(1)
        action_layout.addWidget(self.use_savings_btn)
        action_layout.addWidget(self.edit_transaction_btn)
        action_layout.addWidget(self.delete_btn)
        ledger_layout.addWidget(action_bar)
        self.transaction_list.currentRowChanged.connect(self.update_reclass_ui)
        self.transactions_action_bar = action_bar
        self.use_savings_btn.setEnabled(False)
        self.edit_transaction_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

        self.summary_card = QFrame()
        self.summary_card.setObjectName("Card")
        summary_layout = QVBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(20, 20, 20, 20)
        summary_layout.setSpacing(12)
        summary_header = QLabel("Monthly Summary")
        summary_header.setObjectName("SectionTitle")
        summary_layout.addWidget(summary_header)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)
        today = date.today()
        self.month_combo = QComboBox()
        for month_index in range(1, 13):
            name = date(2000, month_index, 1).strftime("%B")
            self.month_combo.addItem(name, month_index)
        self.month_combo.setCurrentIndex(today.month - 1)
        self.month_combo.currentIndexChanged.connect(self.update_summary)

        self.year_combo = QComboBox()
        for year in range(today.year - 3, today.year + 2):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(today.year))
        self.year_combo.currentIndexChanged.connect(self.update_summary)

        self.compare_checkbox = QCheckBox("Compare with previous month")
        self.compare_checkbox.stateChanged.connect(lambda _: self.update_summary())

        controls_row.addWidget(QLabel("Month:"))
        controls_row.addWidget(self.month_combo)
        controls_row.addWidget(QLabel("Year:"))
        controls_row.addWidget(self.year_combo)
        controls_row.addStretch(1)
        controls_row.addWidget(self.compare_checkbox)
        summary_layout.addLayout(controls_row)

        self.summary_frame = QFrame()
        self.summary_frame.setObjectName("SummaryBubble")
        self.summary_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        summary_inner = QVBoxLayout(self.summary_frame)
        summary_inner.setContentsMargins(18, 16, 18, 16)
        summary_inner.setSpacing(12)

        self.summary_overview_label = QLabel("No transactions recorded yet.")
        self.summary_overview_label.setObjectName("SummaryCaption")
        self.summary_overview_label.setWordWrap(True)
        self.summary_overview_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary_inner.addWidget(self.summary_overview_label)

        kpi_container = QWidget()
        kpi_layout = QGridLayout(kpi_container)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setHorizontalSpacing(12)
        kpi_layout.setVerticalSpacing(12)
        self.kpi_cards = {}
        for col, (metric_key, metric_label) in enumerate(
            [("income", "Income"), ("expense", "Spending"), ("savings", "Savings"), ("net", "Net")]
        ):
            card = QFrame()
            card.setObjectName("SummaryKPI")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 14, 16, 14)
            card_layout.setSpacing(6)
            title = QLabel(metric_label)
            title.setObjectName("SummaryKPIHeader")
            value = QLabel("RM 0.00")
            value.setObjectName("SummaryKPIValue")
            delta = QLabel("Delta pending")
            delta.setObjectName("SummaryKPIDelta")
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            card_layout.addWidget(delta)
            card_layout.addStretch(1)
            kpi_layout.addWidget(card, 0, col)
            self.kpi_cards[metric_key] = {"frame": card, "value": value, "delta": delta}
        summary_inner.addWidget(kpi_container)

        self.summary_category_label = QLabel("Category breakdown will appear once you log spending.")
        self.summary_category_label.setObjectName("SummaryCaption")
        self.summary_category_label.setWordWrap(True)
        self.summary_category_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        summary_inner.addWidget(self.summary_category_label)

        self.category_table = QTableWidget(0, 4)
        self.category_table.setObjectName("SummaryTable")
        self.category_table.setHorizontalHeaderLabels(["Category", "Spent", "Budget", "Variance"])
        v_header = self.category_table.verticalHeader()
        if v_header is not None:
            v_header.setVisible(False)
        self.category_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.category_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.category_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.setSortingEnabled(True)
        header = self.category_table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for col in range(1, 4):
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        summary_inner.addWidget(self.category_table)

        self.forecast_label = QLabel("Forecasts will appear once you log transactions.")
        self.forecast_label.setObjectName("SummaryCaption")
        self.forecast_label.setWordWrap(True)
        summary_inner.addWidget(self.forecast_label)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        sparkline_frame = QFrame()
        sparkline_frame.setObjectName("SummarySubCard")
        sparkline_layout = QVBoxLayout(sparkline_frame)
        sparkline_layout.setContentsMargins(16, 14, 16, 14)
        sparkline_layout.setSpacing(8)
        sparkline_header = QLabel("Daily Spend Sparkline")
        sparkline_header.setObjectName("SummaryCaption")
        sparkline_layout.addWidget(sparkline_header)
        if MATPLOTLIB_AVAILABLE and FigureCanvasQTAgg and Figure:
            figure_cls = cast(type, Figure)
            canvas_cls = cast(type, FigureCanvasQTAgg)
            self.sparkline_fig = figure_cls(figsize=(4.0, 1.4))
            self.sparkline_ax = self.sparkline_fig.add_subplot(111)
            self.sparkline_canvas = canvas_cls(self.sparkline_fig)
            sparkline_layout.addWidget(self.sparkline_canvas)
        else:
            self.sparkline_fig = None
            self.sparkline_ax = None
            self.sparkline_canvas = None
            self.sparkline_placeholder = QLabel("Install matplotlib to view spending sparkline.")
            self.sparkline_placeholder.setObjectName("SummaryText")
            sparkline_layout.addWidget(self.sparkline_placeholder)
        bottom_row.addWidget(sparkline_frame, 3)

        self.alerts_frame = QFrame()
        self.alerts_frame.setObjectName("SummarySubCard")
        alerts_layout = QVBoxLayout(self.alerts_frame)
        alerts_layout.setContentsMargins(16, 14, 16, 14)
        alerts_layout.setSpacing(8)
        alerts_header = QLabel("Alerts")
        alerts_header.setObjectName("SummaryCaption")
        alerts_layout.addWidget(alerts_header)
        self.alerts_list = QListWidget()
        self.alerts_list.setObjectName("SummaryAlerts")
        self.alerts_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.alerts_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        alerts_layout.addWidget(self.alerts_list)
        bottom_row.addWidget(self.alerts_frame, 2)
        self.alerts_frame.hide()

        summary_inner.addLayout(bottom_row)

        self.summary_scroll = QScrollArea()
        self.summary_scroll.setWidgetResizable(True)
        self.summary_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.summary_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.summary_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.summary_scroll.setWidget(self.summary_frame)
        summary_layout.addWidget(self.summary_scroll, 1)

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

        for card in (form_card, budget_card, ledger_card, self.summary_card):
            card.setMinimumWidth(340)
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.cards_workspace = CardWorkspace(columns=2)
        self.cards_workspace.add_card(form_card, tx_header)
        self.cards_workspace.add_card(budget_card, budget_header)
        self.cards_workspace.add_card(ledger_card, ledger_header)
        self.cards_workspace.add_card(self.summary_card, summary_header)
        self.cards_workspace.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.card_frames = [form_card, budget_card, ledger_card, self.summary_card]

        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.cards_scroll.setWidget(self.cards_workspace)

        layout.addWidget(header_wrapper)
        layout.addWidget(self.cards_scroll, 1)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)

        self.income_btn.clicked.connect(lambda: self.handle_add_tx("income"))
        self.expense_btn.clicked.connect(lambda: self.handle_add_tx("expense"))
        self.savings_btn.clicked.connect(lambda: self.handle_add_tx("savings"))
        self.add_budget_btn.clicked.connect(self.add_budget)
        self.export_btn.clicked.connect(self.export_monthly_data)
        self.chart_btn.clicked.connect(self.show_savings_visual)
        self.expense_chart_btn.clicked.connect(self.show_expense_pie_chart)
        self.currency_convert_btn.clicked.connect(self.perform_currency_conversion)
        self.currency_update_btn.clicked.connect(self.refresh_exchange_rates)
        self.use_savings_btn.clicked.connect(self.use_savings_funds)
        self.edit_transaction_btn.clicked.connect(self.edit_selected_transaction)
        self.delete_btn.clicked.connect(self.delete_selected_transaction)

        # Enhance all secondary buttons with shadow effects
        for btn in [self.add_budget_btn, self.use_savings_btn, self.edit_transaction_btn, 
                    self.delete_btn, self.export_btn, self.chart_btn, self.expense_chart_btn,
                    self.currency_convert_btn, self.currency_update_btn]:
            self.enhance_button_with_shadow(btn, blur_radius=12)

        self.refresh_currency_options()
        self.apply_theme()
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        
        # Add smooth entrance animations
        QTimer.singleShot(100, self._animate_entrance)

    def _animate_entrance(self):
        """Animate card entrance with smooth slide-in + fade tweens."""
        cards = getattr(self, 'card_frames', [])
        for idx, card in enumerate(cards):
            # Slide-in from left + fade tween
            pos_anim = QPropertyAnimation(card, b"geometry")
            pos_anim.setDuration(500)
            pos_anim.setEasingCurve(QEasingCurve.OutCubic)
            
            start_geo = card.geometry()
            slide_start = start_geo.translated(-100, 0)  # Start 100px left
            
            pos_anim.setStartValue(slide_start)
            pos_anim.setEndValue(start_geo)
            
            # Fade tween
            effect = QGraphicsOpacityEffect()
            card.setGraphicsEffect(effect)
            fade_anim = QPropertyAnimation(effect, b"opacity")
            fade_anim.setDuration(500)
            fade_anim.setEasingCurve(QEasingCurve.OutQuad)
            fade_anim.setStartValue(0.0)
            fade_anim.setEndValue(1.0)
            
            # Combine animations
            group = QParallelAnimationGroup()
            group.addAnimation(pos_anim)
            group.addAnimation(fade_anim)
            
            # Stagger the start
            QTimer.singleShot(idx * 100, group.start)


    def show_error_popup(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def _build_menu(self):
        menu_bar = self.menuBar()
        if menu_bar is None:
            menu_bar = QMenuBar(self)
            self.setMenuBar(menu_bar)
        menu_bar.clear()

        file_menu = menu_bar.addMenu("&File")
        if file_menu is not None:
            export_csv_action = QAction("Export Monthly CSV", self)
            export_csv_action.triggered.connect(self.export_monthly_data)
            file_menu.addAction(export_csv_action)

            export_png_action = QAction("Export Summary as PNG", self)
            export_png_action.triggered.connect(self.export_summary_as_png)
            file_menu.addAction(export_png_action)

            export_pdf_action = QAction("Export Summary as PDF", self)
            export_pdf_action.triggered.connect(self.export_summary_as_pdf)
            file_menu.addAction(export_pdf_action)

            file_menu.addSeparator()
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.handle_exit)
            file_menu.addAction(exit_action)

        view_menu = menu_bar.addMenu("&View")
        if view_menu is not None:
            toggle_theme_action = QAction("Toggle Light/Dark Mode", self)
            toggle_theme_action.setShortcut(QKeySequence("Ctrl+T"))
            toggle_theme_action.triggered.connect(self.toggle_theme)
            view_menu.addAction(toggle_theme_action)

            toggle_converter_action = QAction("Show Currency Converter", self)
            toggle_converter_action.setCheckable(True)
            toggle_converter_action.setChecked(self.show_converter)
            toggle_converter_action.toggled.connect(self.toggle_currency_converter)
            view_menu.addAction(toggle_converter_action)
            self.toggle_converter_action = toggle_converter_action

    def _install_shortcuts(self):
        QShortcut(QKeySequence("Return"), self, self.submit_default_transaction)
        QShortcut(QKeySequence("Enter"), self, self.submit_default_transaction)
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo_last_transaction)
        QShortcut(QKeySequence("Ctrl+E"), self, self.export_monthly_data)

    def _build_converter_window(self):
        if self.converter_window is not None:
            return
        window = FloatingConverterWindow(self)
        window_type_enum = getattr(Qt, "WindowType", None)
        if window_type_enum is not None and hasattr(window_type_enum, "Window"):
            window_flag_obj = window_type_enum.Window
        else:
            window_flag_obj = getattr(Qt, "Window", 0x00000001)
        if isinstance(window_flag_obj, int):
            window_flag = Qt.WindowType(window_flag_obj)
        else:
            window_flag = cast(Qt.WindowType, window_flag_obj)
        window.setWindowFlag(window_flag, True)
        window.setWindowModality(Qt.WindowModality.NonModal)
        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        window.setObjectName("ConverterWindow")
        window.setWindowTitle("Currency Converter")

        layout = QVBoxLayout(window)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        header = QLabel("Currency Converter")
        header.setObjectName("SectionTitle")
        layout.addWidget(header)

        self.currency_amount_input = QLineEdit()
        self.currency_amount_input.setPlaceholderText("Amount in MYR")
        self.currency_amount_input.setValidator(QDoubleValidator(0.00, 1_000_000.0, 2))
        layout.addWidget(self.currency_amount_input)

        self.currency_target_combo = QComboBox()
        self.currency_target_combo.setEditable(True)
        combo_edit = self.currency_target_combo.lineEdit()
        if combo_edit is not None:
            combo_edit.setPlaceholderText("Search currency (e.g., USD - US Dollar)")
        layout.addWidget(self.currency_target_combo)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        self.currency_convert_btn = QPushButton("Convert")
        self.currency_convert_btn.setObjectName("SecondaryButton")
        self.currency_update_btn = QPushButton("Refresh Rates")
        self.currency_update_btn.setObjectName("SecondaryButton")
        button_row.addWidget(self.currency_convert_btn)
        button_row.addWidget(self.currency_update_btn)
        layout.addLayout(button_row)

        self.currency_result_label = QLabel("Result: -")
        self.currency_result_label.setWordWrap(True)
        layout.addWidget(self.currency_result_label)

        self.currency_info_label = QLabel("Rates last updated: -")
        self.currency_info_label.setObjectName("InfoText")
        self.currency_info_label.setWordWrap(True)
        layout.addWidget(self.currency_info_label)

        window.closed.connect(self._on_converter_window_closed)
        self.converter_window = window
        window.adjustSize()
        self._position_converter_window()
        if self.show_converter:
            window.show()
        else:
            window.hide()

    def _position_converter_window(self):
        window = self.converter_window
        if window is None:
            return
        size = window.size()
        if size.isEmpty():
            size = window.sizeHint()
        main_geo = self.frameGeometry()
        x = main_geo.center().x() - size.width() // 2
        y = main_geo.top() + 60
        # Keep window on-screen by clamping to available geometry
        screen = QApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            x = max(available.left() + 20, min(x, available.right() - size.width() - 20))
            y = max(available.top() + 20, min(y, available.bottom() - size.height() - 20))
        window.move(x, y)

    def _on_converter_window_closed(self):
        self.show_converter = False
        if self.toggle_converter_action is not None and self.toggle_converter_action.isChecked():
            self.toggle_converter_action.blockSignals(True)
            self.toggle_converter_action.setChecked(False)
            self.toggle_converter_action.blockSignals(False)
        self.toast("Currency converter hidden.")

    def _refresh_card_shadows(self):
        frames = getattr(self, "card_frames", [])
        if not frames:
            return
        shadow_strength = 140 if self.theme_mode == "dark" else 80
        for frame in frames:
            if frame is None:
                continue
            effect = frame.graphicsEffect()
            if not isinstance(effect, QGraphicsDropShadowEffect):
                effect = QGraphicsDropShadowEffect(frame)
            effect.setBlurRadius(28)
            effect.setOffset(0, 12)
            effect.setColor(QColor(0, 0, 0, shadow_strength))
            frame.setGraphicsEffect(effect)
        action_bar = getattr(self, "transactions_action_bar", None)
        if isinstance(action_bar, QFrame):
            effect = action_bar.graphicsEffect()
            if not isinstance(effect, QGraphicsDropShadowEffect):
                effect = QGraphicsDropShadowEffect(action_bar)
            effect.setBlurRadius(18)
            effect.setOffset(0, 6)
            effect.setColor(QColor(0, 0, 0, max(shadow_strength - 40, 30)))
            action_bar.setGraphicsEffect(effect)

    def moveEvent(self, a0: QMoveEvent) -> None:
        event = a0
        super().moveEvent(event)
        window = self.converter_window
        if window is not None and window.isVisible():
            self._position_converter_window()

    def resizeEvent(self, a0: QResizeEvent) -> None:
        event = a0
        super().resizeEvent(event)
        window = self.converter_window
        if window is not None and window.isVisible():
            self._position_converter_window()

    def toggle_currency_converter(self, checked: bool):
        self.show_converter = bool(checked)
        if self.toggle_converter_action is not None and self.toggle_converter_action.isChecked() != self.show_converter:
            self.toggle_converter_action.blockSignals(True)
            self.toggle_converter_action.setChecked(self.show_converter)
            self.toggle_converter_action.blockSignals(False)
        if self.converter_window is None:
            self._build_converter_window()
        window = self.converter_window
        if window is None:
            return
        if self.show_converter:
            window.show()
            window.raise_()
            window.activateWindow()
            self._position_converter_window()
        else:
            window.hide()

    def toast(self, message: str, timeout_ms: int = 4000):
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(message, timeout_ms)

    def _get_chart_window(self, key: str, title: str, help_text: str) -> ChartWindow:
        window = self.chart_windows.get(key)
        if window is None:
            window = ChartWindow(title=title, help_text=help_text, parent=self)
            window.setStyleSheet(self.styleSheet())
            window.apply_theme(self.theme_mode)
            self._apply_titlebar_palette(window)

            def _cleanup(_=None, chart_key=key):
                self.chart_windows.pop(chart_key, None)

            window.destroyed.connect(_cleanup)
            self.chart_windows[key] = window
        else:
            window.setWindowTitle(title)
            window.set_help_text(help_text)
        window.setStyleSheet(self.styleSheet())
        window.apply_theme(self.theme_mode)
        self._apply_titlebar_palette(window)
        return window

    def handle_exit(self):
        self.close()

    def createGradientButton(self, text, color1, color2):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:1 {color2});
                border: none; 
                color: white; 
                border-radius: 10px; 
                padding: 10px 16px;
                font-weight: bold; 
                font-size: 12pt;
                transition: all 0.2s ease-out;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self._lighten_color(color1)}, stop:1 {self._lighten_color(color2)});
                padding: 9px 16px;
            }}
            QPushButton:pressed {{ 
                padding: 11px 16px;
            }}
        """)
        
        # Enhanced shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        btn.setGraphicsEffect(shadow)
        return btn
    
    def _lighten_color(self, hex_color):
        """Lighten a hex color by 15%."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c * 1.15)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
    
    def enhance_button_with_shadow(self, button: QPushButton, blur_radius: int = 18):
        """Add shadow and smooth hover effects to any button."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur_radius)
        shadow.setColor(QColor(0, 0, 0, 140))
        shadow.setOffset(0, 2)
        button.setGraphicsEffect(shadow)
        button.setCursor(Qt.CursorShape.PointingHandCursor)

    def _progress_stylesheet(self, chunk_color: str, disabled: bool = False) -> str:
        dark = self.theme_mode == "dark"
        track_color = "#1C1C23" if dark else "#F3F5F9"
        border_color = "#30303C" if dark else "#D3D7E0"
        text_color = "#A0A7B5" if disabled else ("#E0E0E0" if dark else "#212121")
        chunk = "#3E414D" if disabled else chunk_color
        return (
            "QProgressBar {"
            f" background-color: {track_color};"
            f" border: 1px solid {border_color};"
            " border-radius: 9px;"
            " text-align: center;"
            f" color: {text_color};"
            "}"
            "QProgressBar::chunk:horizontal {"
            f" background-color: {chunk};"
            " border-radius: 8px;"
            " border-top-left-radius: 8px;"
            " border-bottom-left-radius: 8px;"
            " border-top-right-radius: 8px;"
            " border-bottom-right-radius: 8px;"
            " margin: 1px;"
            " margin-left: 0px;"
            "}"
        )

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
                    elif tx["type"] == "expense":
                        self.balance -= tx["amount"]
                    else:
                        # Savings are neutral (transfer) - do not change balance
                        pass
        except FileNotFoundError:
            self.show_error_popup("Error", "Ledger file not found!")
            return

        for tx in self.transactions:
            sign = "+" if tx["type"] == "income" else "-"
            tx_id = tx["tx_id"] or "-"
            display_amount = abs(tx["amount"])
            display = f"{tx['date']} | {tx['category']} | {sign} RM{display_amount:.2f} | {tx['desc']}  ({tx_id})"
            self.transaction_list.addItem(display)
        self.refresh_period_controls()
        self.update_reclass_ui(self.transaction_list.currentRow())
        self.update_use_savings_button()

    def current_month_transactions(
        self,
        type_filter: str | None = None,
        year: int | None = None,
        month: int | None = None,
    ) -> list[dict]:
        if year is None or month is None:
            selected_year, selected_month = self._selected_period()
            if year is None:
                year = selected_year
            if month is None:
                month = selected_month
        matches: list[dict] = []
        for tx in self.transactions:
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year != year or tx_date.month != month:
                continue
            if type_filter and tx["type"] != type_filter:
                continue
            matches.append(tx)
        return matches

    def update_use_savings_button(self):
        if not hasattr(self, "use_savings_btn"):
            return
        totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for tx in self.transactions:
            if tx["type"] == "savings":
                category = tx["category"] or "Savings"
                totals[category] += tx["amount"]
        has_available = any(amount > 0 for amount in totals.values())
        self.use_savings_btn.setEnabled(has_available)

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

        today_spend = {cat: self.category_monthly_expense_total(cat) for cat in self.budget_map}
        for category in sorted(self.budget_map.keys()):
            allowance = self.budget_map[category]
            spent = today_spend.get(category, Decimal("0.00"))
            used_percent = (spent / allowance * Decimal("100.00")) if allowance > 0 else Decimal("0.00")
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, category)
            widget = QWidget()
            widget_layout = QVBoxLayout(widget)
            widget_layout.setContentsMargins(12, 8, 12, 8)
            widget_layout.setSpacing(4)
            title = QLabel(category)
            title.setObjectName("SummaryCaption")
            detail = QLabel(f"RM {spent:.2f} of RM {allowance:.2f}")
            detail.setObjectName("SummaryText")
            progress = QProgressBar()
            progress.setRange(0, 150)
            progress.setValue(min(int(used_percent) if allowance > 0 else 0, 150))
            progress.setFormat(f"{used_percent:.0f}%" if allowance > 0 else "N/A")
            if allowance == 0:
                progress.setEnabled(False)
                chunk_color = "#4F525E"
            elif used_percent > 100:
                chunk_color = "#E57373"
            elif used_percent >= 80:
                chunk_color = "#FFB74D"
            else:
                chunk_color = "#64B5F6"
            progress.setStyleSheet(self._progress_stylesheet(chunk_color, allowance == 0))
            widget_layout.addWidget(title)
            widget_layout.addWidget(detail)
            widget_layout.addWidget(progress)
            item.setSizeHint(widget.sizeHint())
            self.budget_list.addItem(item)
            self.budget_list.setItemWidget(item, widget)

    def edit_budget_item(self, item: QListWidgetItem):
        if item is None:
            return
        category = item.data(Qt.ItemDataRole.UserRole)
        if not category:
            return
        current_amount = self.budget_map.get(category, Decimal("0.00"))
        text, ok = QInputDialog.getText(
            self,
            "Edit Budget",
            f"Monthly budget for {category}",
            text=f"{current_amount:.2f}",
        )
        if not ok:
            return
        try:
            amount = money(text.strip())
            if amount < 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Invalid amount", "Enter a valid budget amount, e.g. 250.00")
            return
        self.budget_map[category] = amount
        self.save_budgets()
        self.load_budgets()
        self.update_summary()
        self.toast(f"{category} budget updated.")

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

    def refresh_period_controls(self):
        if not hasattr(self, "year_combo"):
            return
        years = set()
        for tx in self.transactions:
            try:
                years.add(date.fromisoformat(tx["date"]).year)
            except ValueError:
                continue
        if not years:
            years = {date.today().year}
        years = sorted(years)
        current_year_text = self.year_combo.currentText()
        current_year = int(current_year_text) if current_year_text.isdigit() else years[-1]
        self.year_combo.blockSignals(True)
        self.year_combo.clear()
        for yr in years:
            self.year_combo.addItem(str(yr))
        if current_year in years:
            self.year_combo.setCurrentText(str(current_year))
        else:
            self.year_combo.setCurrentText(str(years[-1]))
        self.year_combo.blockSignals(False)

    def _selected_period(self) -> tuple[int, int]:
        today = date.today()
        month = today.month
        year = today.year
        if hasattr(self, "month_combo"):
            data = self.month_combo.currentData()
            month = int(data) if data else month
        if hasattr(self, "year_combo"):
            text = self.year_combo.currentText()
            if text.isdigit():
                year = int(text)
        return year, month

    @staticmethod
    def _previous_period(year: int, month: int) -> tuple[int, int]:
        if month == 1:
            return year - 1, 12
        return year, month - 1

    def _aggregate_month(self, year: int, month: int):
        totals = {
            "income": Decimal("0.00"),
            "expense": Decimal("0.00"),
            "savings": Decimal("0.00"),
            "savings_balance": Decimal("0.00"),
        }
        category_totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        daily_expense: defaultdict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
        month_transactions: list[tuple[dict, date]] = []
        month_end = date(year, month, calendar.monthrange(year, month)[1])

        for tx in self.transactions:
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year != year or tx_date.month != month:
                continue
            month_transactions.append((tx, tx_date))
            amount = tx["amount"]
            ttype = tx["type"]
            category = tx["category"] or "Uncategorised"
            if ttype == "income":
                totals["income"] += amount
            elif ttype == "savings":
                # Savings should not appear in the expense category breakdown
                # Track savings total only; exclude from category_totals and daily expense
                totals["savings"] += amount
            else:
                totals["expense"] += amount
                category_totals[category] += amount
                daily_expense[tx_date.day] += amount

        savings_balance = Decimal("0.00")
        for tx in self.transactions:
            if tx["type"] != "savings":
                continue
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date > month_end:
                continue
            savings_balance += tx["amount"]

        totals["savings_balance"] = savings_balance

        return totals, category_totals, month_transactions, daily_expense

    def _update_kpi_cards(
        self,
        totals: dict,
        prev_totals: dict | None,
        compare_enabled: bool,
        prev_month_label: str,
    ) -> None:
        if not hasattr(self, "kpi_cards"):
            return
        savings_display = totals.get("savings_balance", totals["savings"])
        metrics = {
            "income": totals["income"],
            "expense": totals["expense"],
            "savings": savings_display,
            "net": totals["income"] - totals["expense"],
        }
        for key, value in metrics.items():
            card = self.kpi_cards.get(key)
            if not card:
                continue
            value_label: QLabel = card["value"]
            delta_label: QLabel = card["delta"]
            value_label.setText(f"RM {value:.2f}")
            if key == "net":
                net_color = "#81C784" if value >= 0 else "#E57373"
                value_label.setStyleSheet(f"color: {net_color};")
            else:
                value_label.setStyleSheet("")
            if compare_enabled and prev_totals is not None:
                if key == "savings":
                    previous_value = prev_totals.get(
                        "savings_balance",
                        prev_totals.get("savings", Decimal("0.00")),
                    )
                else:
                    previous_value = prev_totals.get(key, Decimal("0.00"))
                diff = value - previous_value
                if diff > Decimal("0.00"):
                    arrow, color = "▲", "#81C784"
                    if key == "expense":
                        color = "#FFB74D"
                elif diff < Decimal("0.00"):
                    arrow, color = "▼", "#E57373"
                else:
                    arrow, color = "■", "#B0BEC5"
                delta_label.setText(f"{arrow} RM {abs(diff):.2f} vs {prev_month_label}")
                delta_label.setStyleSheet(f"color: {color};")
            else:
                delta_label.setText("--")
                delta_label.setStyleSheet("")

    def _populate_category_table(
        self,
        category_totals: defaultdict,
        year: int,
        month: int,
        savings_only_categories: set[str] | None = None,
    ) -> None:
        if not hasattr(self, "category_table"):
            return
        table = self.category_table
        table.setSortingEnabled(False)
        table.setRowCount(0)
        if not category_totals:
            table.setSortingEnabled(True)
            return
        for row, category in enumerate(sorted(category_totals.keys(), key=str.lower)):
            spent = category_totals[category]
            is_savings_only = (
                savings_only_categories is not None and category in savings_only_categories
            )
            budget = None if is_savings_only else self.budget_map.get(category)
            variance = (budget - spent) if budget else None
            used_percent = (spent / budget * Decimal("100.00")) if budget and budget != Decimal("0.00") else None

            table.insertRow(row)
            name_item = QTableWidgetItem(category)
            name_item.setData(Qt.ItemDataRole.UserRole, category.lower())
            table.setItem(row, 0, name_item)

            spent_item = QTableWidgetItem(f"RM {spent:.2f}")
            spent_item.setData(Qt.ItemDataRole.UserRole, float(spent))
            table.setItem(row, 1, spent_item)

            if budget:
                budget_item = QTableWidgetItem(f"RM {budget:.2f}")
                budget_item.setData(Qt.ItemDataRole.UserRole, float(budget))
            else:
                budget_item = QTableWidgetItem("--")
                budget_item.setData(Qt.ItemDataRole.UserRole, -1)
            table.setItem(row, 2, budget_item)

            if variance is not None:
                variance_item = QTableWidgetItem(f"RM {variance:.2f}")
                variance_item.setData(Qt.ItemDataRole.UserRole, float(variance))
            else:
                variance_item = QTableWidgetItem("--")
                variance_item.setData(Qt.ItemDataRole.UserRole, -1)
            table.setItem(row, 3, variance_item)

            if used_percent is not None:
                tooltip = f"Used {used_percent:.0f}% of budget"
                for item in (name_item, spent_item, budget_item, variance_item):
                    item.setToolTip(tooltip)

            if used_percent is not None and used_percent > 100:
                color = QColor("#E57373")
            elif used_percent is not None and used_percent >= 80:
                color = QColor("#FFB74D")
            else:
                color = None
            if color:
                for col in range(4):
                    item = table.item(row, col)
                    if item is not None:
                        item.setForeground(color)

        table.setSortingEnabled(True)
        table.sortItems(1, Qt.SortOrder.DescendingOrder)

    def _update_sparkline(self, daily_expense: defaultdict, year: int, month: int) -> None:
        if (
            not MATPLOTLIB_AVAILABLE
            or not hasattr(self, "sparkline_canvas")
            or self.sparkline_canvas is None
            or self.sparkline_fig is None
        ):
            if hasattr(self, "sparkline_placeholder"):
                self.sparkline_placeholder.setText("Install matplotlib to view spending sparkline.")
            return
        days_in_month = calendar.monthrange(year, month)[1]
        cumulative = []
        running = Decimal("0.00")
        x_values = []
        for day in range(1, days_in_month + 1):
            running += daily_expense.get(day, Decimal("0.00"))
            cumulative.append(float(running))
            x_values.append(day)
        fig = self.sparkline_fig
        canvas = self.sparkline_canvas
        if fig is None or canvas is None or not hasattr(fig, "add_subplot"):
            return
        fig.clear()
        ax = fig.add_subplot(111)
        self.sparkline_ax = ax
        line_color = "#4CAF50" if self.theme_mode == "light" else "#81C784"
        ax.plot(x_values, cumulative, color=line_color, linewidth=2.2)
        ax.fill_between(x_values, cumulative, color=line_color, alpha=0.15)
        ax.set_xlim(1, max(1, days_in_month))
        max_value = max(cumulative) if cumulative else 0
        ax.set_ylim(bottom=0, top=max(1, max_value * 1.1 if max_value else 1))
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_facecolor("none")
        fig.patch.set_facecolor("none")
        canvas.draw_idle()

    def _update_alerts(self, category_totals: defaultdict, month_transactions: list[tuple[dict, date]]) -> None:
        if not hasattr(self, "alerts_frame") or self.alerts_frame is None or self.alerts_list is None:
            return
        alerts: list[str] = []
        for category, spent in category_totals.items():
            budget = self.budget_map.get(category)
            if budget and spent > budget:
                over = spent - budget
                alerts.append(f"{category} over budget by RM {over:.2f}")
        today = date.today()
        for tx, tx_date in month_transactions:
            category = (tx["category"] or "").lower()
            desc = (tx["desc"] or "").lower()
            if "subscription" in category or "subscription" in desc or "due" in desc:
                next_due = tx_date + timedelta(days=30)
                days_until = (next_due - today).days
                if 0 <= days_until <= 3:
                    alerts.append(
                        f"{tx['category'] or 'Subscription'} billing due in {days_until} day(s) ({tx['desc']})"
                    )
        unique_alerts = []
        seen = set()
        for alert in alerts:
            if alert not in seen:
                seen.add(alert)
                unique_alerts.append(alert)
        self.alerts_list.clear()
        if unique_alerts:
            for alert in unique_alerts:
                self.alerts_list.addItem(f"- {alert}")
            self.alerts_frame.show()
        else:
            self.alerts_frame.hide()

    def _update_forecast(self, totals: dict, month_transactions: list[tuple[dict, date]], year: int, month: int) -> None:
        if not hasattr(self, "forecast_label"):
            return
        today = date.today()
        if year != today.year or month != today.month:
            self.forecast_label.setText("Forecasts shown for the current month only.")
            return
        days_in_month = Decimal(calendar.monthrange(year, month)[1])
        current_transactions = [(tx, tx_date) for tx, tx_date in month_transactions if tx_date <= today]
        if not current_transactions:
            self.forecast_label.setText("Forecast month-end: RM 0.00 | Safe-to-spend today: RM 0.00")
            return
        days_elapsed = Decimal(today.day)
        days_remaining = max(Decimal("0.00"), days_in_month - days_elapsed)
        expense = sum((tx["amount"] for tx, tx_date in current_transactions if tx["type"] == "expense"), Decimal("0.00"))
        income = sum((tx["amount"] for tx, tx_date in current_transactions if tx["type"] == "income"), Decimal("0.00"))
        daily_burn = expense / days_elapsed if days_elapsed > 0 else Decimal("0.00")
        projected_spend = expense + (daily_burn * days_remaining)
        net_forecast = income - projected_spend
        if days_remaining > 0:
            safe_to_spend = (income - expense) / days_remaining
        else:
            safe_to_spend = income - expense
        self.forecast_label.setText(
            f"Forecast month-end: RM {net_forecast:.2f} | Safe-to-spend today: RM {safe_to_spend:.2f}"
        )
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
        if not hasattr(self, "summary_overview_label"):
            return
        year, month = self._selected_period()
        month_date = date(year, month, 1)
        month_label = month_date.strftime("%B %Y")
        totals, category_totals, month_transactions, daily_expense = self._aggregate_month(year, month)
        transaction_count = len(month_transactions)
        net_value = totals["income"] - totals["expense"] - totals["savings"]
        overview_text = (
            f"<b>{month_label}</b> &bull; {transaction_count} transaction{'s' if transaction_count != 1 else ''} "
            f"&bull; Net RM {net_value:.2f}"
        )
        self.summary_overview_label.setText(overview_text)

        if category_totals:
            self.summary_category_label.setText(
                f"Category breakdown for {month_date.strftime('%B')} ({len(category_totals)} categories)"
            )
        else:
            self.summary_category_label.setText("Category breakdown will appear once you log spending.")

        compare_enabled = hasattr(self, "compare_checkbox") and self.compare_checkbox.isChecked()
        if compare_enabled:
            prev_year, prev_month = self._previous_period(year, month)
            prev_totals, _, _, _ = self._aggregate_month(prev_year, prev_month)
            prev_label = date(prev_year, prev_month, 1).strftime("%b")
        else:
            prev_totals = None
            prev_label = ""
        self._update_kpi_cards(totals, prev_totals, compare_enabled, prev_label)
        expense_cats = set()
        savings_cats = set()
        for tx, _tx_date in month_transactions:
            cat = tx.get("category") or ("Savings" if tx.get("type") == "savings" else "General")
            if tx.get("type") == "expense":
                expense_cats.add(cat)
            elif tx.get("type") == "savings":
                savings_cats.add(cat)
        savings_only = savings_cats - expense_cats
        self._populate_category_table(category_totals, year, month, savings_only)
        self._update_alerts(category_totals, month_transactions)
        self._update_sparkline(daily_expense, year, month)
        self._update_forecast(totals, month_transactions, year, month)

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

    def category_monthly_expense_total(self, category: str) -> Decimal:
        today = date.today()
        total = Decimal("0.00")
        for tx in self.transactions:
            if tx["category"] != category:
                continue
            if tx["type"] != "expense":
                continue
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date.year == today.year and tx_date.month == today.month:
                total += tx["amount"]
        return total

    def update_reclass_ui(self, row: int):
        has_selection = 0 <= row < len(self.transactions)
        if hasattr(self, "delete_btn"):
            self.delete_btn.setEnabled(has_selection)
        if hasattr(self, "edit_transaction_btn"):
            self.edit_transaction_btn.setEnabled(has_selection)

    def open_transaction_context_menu(self, position: QPoint):
        row = self.transaction_list.indexAt(position).row()
        if row < 0 or row >= len(self.transactions):
            return
        menu = QMenu(self)
        edit_action = menu.addAction("Edit...")
        duplicate_action = menu.addAction("Duplicate")
        delete_action = menu.addAction("Delete")
        action = menu.exec_(self.transaction_list.mapToGlobal(position))
        if action == edit_action:
            self.edit_transaction(row)
        elif action == duplicate_action:
            self.duplicate_transaction(row)
        elif action == delete_action:
            self.delete_transaction(row)

    def edit_transaction(self, row: int):
        if row < 0 or row >= len(self.transactions):
            return
        tx = self.transactions[row]
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Transaction")
        layout = QVBoxLayout(dialog)

        form = QFormLayout()
        type_combo = QComboBox()
        type_combo.addItems(["income", "expense", "savings"])
        current_index = type_combo.findText(tx["type"])
        if current_index >= 0:
            type_combo.setCurrentIndex(current_index)

        amount_edit = QLineEdit(f"{tx['amount']:.2f}")
        amount_edit.setValidator(QDoubleValidator(0.01, 1_000_000.0, 2))
        category_edit = QLineEdit(tx["category"])
        desc_edit = QLineEdit(tx["desc"])

        form.addRow("Type", type_combo)
        form.addRow("Amount (RM)", amount_edit)
        form.addRow("Category", category_edit)
        form.addRow("Description", desc_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() != QDialog.Accepted:
            return

        try:
            amount_val = money(amount_edit.text().strip())
            if amount_val <= 0:
                raise ValueError
        except Exception:
            QMessageBox.warning(self, "Invalid amount", "Enter a valid amount, e.g. 42.00")
            return

        updated = self.update_transaction_record(
            tx["tx_id"],
            new_type=type_combo.currentText(),
            new_category=category_edit.text().strip(),
            new_amount=amount_val,
            new_desc=desc_edit.text().strip(),
        )
        if not updated:
            QMessageBox.critical(self, "Update failed", "Could not update the transaction in the ledger file.")
            return
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.transaction_list.setCurrentRow(row)
        self.toast("Transaction updated.")

    def duplicate_transaction(self, row: int):
        if row < 0 or row >= len(self.transactions):
            return
        tx = self.transactions[row]
        txid = next_tx_id()
        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([txid, tx["date"], tx["type"], tx["category"], f"{tx['amount']:.2f}", tx["desc"]])
        ensure_private_file(LEDGER_CSV)
        self.undo_stack.append(("transaction", txid))
        self.undo_stack = self.undo_stack[-20:]
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.toast("Transaction duplicated.")

    def delete_transaction(self, row: int):
        if row < 0 or row >= len(self.transactions):
            return
        tx = self.transactions[row]
        confirm = QMessageBox.question(
            self,
            "Delete transaction",
            f"Remove transaction {tx['tx_id']}?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        if not self._remove_transaction_by_id(tx["tx_id"]):
            QMessageBox.critical(self, "Delete failed", "Unable to remove the transaction.")
            return
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        if self.transaction_list.count() > 0:
            next_row = min(row, self.transaction_list.count() - 1)
            self.transaction_list.setCurrentRow(next_row)
        else:
            self.update_reclass_ui(-1)
        self.toast("Transaction deleted.")

    def delete_selected_transaction(self):
        if not hasattr(self, "transaction_list"):
            return
        row = self.transaction_list.currentRow()
        if row < 0 or row >= len(self.transactions):
            QMessageBox.information(self, "Select a transaction", "Choose a transaction to delete.")
            return
        self.delete_transaction(row)

    def edit_selected_transaction(self):
        if not hasattr(self, "transaction_list"):
            return
        row = self.transaction_list.currentRow()
        if row < 0 or row >= len(self.transactions):
            QMessageBox.information(self, "Select a transaction", "Choose a transaction to edit.")
            return
        self.edit_transaction(row)

    def use_savings_funds(self):
        if not self.transactions:
            QMessageBox.information(self, "No savings available", "Record savings deposits before using them.")
            return
        savings_totals: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0.00"))
        for tx in self.transactions:
            if tx["type"] != "savings":
                continue
            category = tx["category"] or "Savings"
            savings_totals[category] += tx["amount"]
        available_totals = {cat: amt for cat, amt in savings_totals.items() if amt > 0}
        if not available_totals:
            QMessageBox.information(
                self,
                "No savings available",
                "All savings have been used. Add new savings deposits before withdrawing.",
            )
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Use Savings")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        amount_edit = QLineEdit()
        amount_edit.setPlaceholderText("Amount to use (RM)")
        amount_edit.setValidator(QDoubleValidator(0.01, 1_000_000.0, 2))
        form.addRow("Amount (RM)", amount_edit)

        savings_combo = QComboBox()
        savings_combo.addItems(sorted(available_totals.keys(), key=str.lower))
        form.addRow("From savings category", savings_combo)

        available_label = QLabel()
        available_label.setObjectName("InfoText")
        form.addRow("Available", available_label)

        expense_combo = QComboBox()
        expense_combo.setEditable(True)
        existing_categories = sorted({cat for cat in self.categories if cat}, key=str.lower)
        for cat in existing_categories:
            if expense_combo.findText(cat) == -1:
                expense_combo.addItem(cat)
        if expense_combo.findText("General") == -1:
            expense_combo.insertItem(0, "General")
        expense_combo.setCurrentText("General")
        form.addRow("Expense category", expense_combo)

        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Description (optional)")
        form.addRow("Description", desc_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        def refresh_available():
            category = savings_combo.currentText().strip() or "Savings"
            amount = available_totals.get(category, Decimal("0.00"))
            available_label.setText(f"RM {amount:.2f}")

        savings_combo.currentIndexChanged.connect(refresh_available)
        refresh_available()

        if dialog.exec_() != QDialog.Accepted:
            return

        amount_text = amount_edit.text().strip()
        if not amount_text:
            QMessageBox.warning(self, "Amount required", "Enter an amount to withdraw.")
            return
        try:
            amount = money(amount_text)
            if amount <= 0:
                raise ValueError
        except Exception:
            QMessageBox.critical(self, "Invalid amount", "Enter a valid amount, e.g. 150.00")
            return

        savings_category = savings_combo.currentText().strip() or "Savings"
        available_amount = available_totals.get(savings_category, Decimal("0.00"))
        if amount > available_amount:
            QMessageBox.warning(
                self,
                "Not enough savings",
                f"Only RM {available_amount:.2f} is available in {savings_category}.",
            )
            return

        expense_category = expense_combo.currentText().strip() or "General"
        description = desc_edit.text().strip() or f"Used savings for {expense_category}"

        first_tx_id = next_tx_id()
        try:
            base_number = int(first_tx_id[2:])
        except ValueError:
            base_number = 0
        second_tx_id = f"TX{base_number + 1:03d}"
        today_str = date.today().isoformat()

        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [first_tx_id, today_str, "savings", savings_category, f"{-amount:.2f}", f"Withdrawal: {description}"]
            )
            writer.writerow(
                [second_tx_id, today_str, "expense", expense_category, f"{amount:.2f}", description]
            )
        ensure_private_file(LEDGER_CSV)

        self.undo_stack.append(("transaction", second_tx_id))
        self.undo_stack.append(("transaction", first_tx_id))
        self.undo_stack = self.undo_stack[-20:]

        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.toast("Savings applied to expense.")

    def _remove_transaction_by_id(self, tx_id: str) -> bool:
        if not tx_id:
            return False
        try:
            with LEDGER_CSV.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                header = reader.fieldnames or LEDGER_HEADER
        except FileNotFoundError:
            return False
        remaining = [row for row in rows if row.get("tx_id") != tx_id]
        if len(remaining) == len(rows):
            return False
        ensure_writable(LEDGER_CSV)
        with LEDGER_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in remaining:
                writer.writerow({field: row.get(field, "") for field in header})
        ensure_private_file(LEDGER_CSV)
        return True

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

    def export_summary_as_png(self):
        if not hasattr(self, "summary_card"):
            QMessageBox.warning(self, "Summary unavailable", "The summary panel is not ready yet.")
            return
        year, month = self._selected_period()
        suggested = Path.home() / f"finfix_summary_{year}_{month:02d}.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Summary as PNG",
            str(suggested),
            "PNG Files (*.png)",
        )
        if not file_path:
            return
        pixmap = self.summary_card.grab()
        if not pixmap.save(file_path, "PNG"):
            QMessageBox.critical(self, "Export failed", "Unable to save the summary as PNG.")
            return
        self.toast(f"Summary image exported to {file_path}")

    def export_summary_as_pdf(self):
        if not hasattr(self, "summary_card"):
            QMessageBox.warning(self, "Summary unavailable", "The summary panel is not ready yet.")
            return
        year, month = self._selected_period()
        suggested = Path.home() / f"finfix_summary_{year}_{month:02d}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Summary as PDF",
            str(suggested),
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        painter = QPainter(printer)
        pixmap = self.summary_card.grab()
        rect = painter.viewport()
        size = pixmap.size()
        size.scale(rect.size(), Qt.AspectRatioMode.KeepAspectRatio)
        painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
        painter.setWindow(pixmap.rect())
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        self.toast(f"Summary PDF exported to {file_path}")

    def export_monthly_data(self):
        year, month = self._selected_period()
        monthly = self.current_month_transactions(year=year, month=month)
        if not monthly:
            QMessageBox.information(self, "Nothing to export", "No transactions recorded for the selected month.")
            return
        default_name = f"finfix_transactions_{year}_{month:02d}.csv"
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
        self.toast(f"Monthly data exported to {file_path}")

    def show_savings_visual(self):
        year, month = self._selected_period()
        last_day = calendar.monthrange(year, month)[1]
        period_end = date(year, month, last_day)
        savings_entries: list[dict] = []
        for tx in self.transactions:
            if tx.get("type") != "savings":
                continue
            try:
                tx_date = date.fromisoformat(tx["date"])
            except ValueError:
                continue
            if tx_date > period_end:
                continue
            savings_entries.append(tx)
        if not savings_entries:
            QMessageBox.information(
                self,
                "No savings recorded",
                "Log savings transactions to view the chart.",
            )
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
        for tx in savings_entries:
            category = tx["category"] or "Savings"
            totals[category] += tx["amount"]
        positive_totals = {cat: amt for cat, amt in totals.items() if amt > Decimal("0.00")}
        if not positive_totals:
            QMessageBox.information(
                self,
                "No savings balance",
                "All savings have been used for the selected period.",
            )
            return
        categories = sorted(positive_totals.keys(), key=str.lower)
        values = [float(positive_totals[cat]) for cat in categories]

        period_label = date(year, month, 1).strftime("%B %Y")
        dark_mode = getattr(self, "theme_mode", "dark") == "dark"
        text_color = "#E0E0E0" if dark_mode else "#212121"
        background_color = "#121212" if dark_mode else "#FFFFFF"
        axes_color = "#1C1C21" if dark_mode else "#FFFFFF"

        fig = Figure(figsize=(6, 4))
        fig.patch.set_facecolor(background_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(axes_color)

        max_value = max(values) if values else 0.0
        if max_value <= 0:
            QMessageBox.information(
                self,
                "No savings balance",
                "All savings have been used for the selected period.",
            )
            return

        try:
            from matplotlib.patches import Rectangle
        except Exception:
            QMessageBox.warning(
                self,
                "Visualization unavailable",
                "matplotlib is required to render charts.\nInstall it with: pip install matplotlib",
            )
            return

        outline_color = "#29B6F6" if dark_mode else "#1565C0"
        battery_height = 0.6
        tip_width = max(max_value * 0.04, 0.25)
        y_positions = list(range(len(categories)))

        def level_color(value: float) -> str:
            if max_value <= 0:
                return "#90A4AE"
            ratio = value / max_value
            if ratio >= 0.75:
                return "#4CAF50" if dark_mode else "#2E7D32"
            if ratio >= 0.4:
                return "#FFD740" if dark_mode else "#F9A825"
            return "#FF7043" if dark_mode else "#E64A19"

        ax.set_title(f"Monthly Savings ({period_label})", color=text_color)
        ax.set_yticks(y_positions)
        ax.set_yticklabels(categories, color=text_color, fontsize=9)
        ax.set_xticks([])
        ax.set_xlim(0, max_value + tip_width + max_value * 0.15)
        ax.set_ylim(-0.75, len(categories) - 0.25)
        ax.tick_params(axis="y", colors=text_color, length=0)
        ax.tick_params(axis="x", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Draw each savings category as a battery-style cell.
        for idx, value in enumerate(values):
            y_center = y_positions[idx]
            bottom = y_center - battery_height / 2
            outline = Rectangle(
                (0, bottom),
                max_value,
                battery_height,
                linewidth=2,
                edgecolor=outline_color,
                facecolor="none",
            )
            ax.add_patch(outline)
            tip = Rectangle(
                (max_value, y_center - battery_height / 4),
                tip_width,
                battery_height / 2,
                linewidth=0,
                facecolor=outline_color,
            )
            ax.add_patch(tip)
            fill_height = battery_height - 0.12
            fill_bottom = bottom + (battery_height - fill_height) / 2
            fill = Rectangle(
                (0, fill_bottom),
                value,
                fill_height,
                linewidth=0,
                facecolor=level_color(value),
            )
            ax.add_patch(fill)
            label_inside = value > max_value * 0.35
            if label_inside:
                label_x = value - max_value * 0.02
                label_align = "right"
            else:
                label_x = value + max_value * 0.02
                label_align = "left"
            label_color = text_color
            if label_inside and not dark_mode:
                label_color = "#FFFFFF"
            ax.text(
                label_x,
                y_center,
                f"RM {value:.2f}",
                va="center",
                ha=label_align,
                color=label_color,
                fontsize=9,
            )

        fig.tight_layout()

        help_text = (
            "Each battery shows cumulative savings per category up to the selected month. "
            "The fill level reflects deposits minus any withdrawals recorded for that category."
        )
        window = self._get_chart_window(
            "savings_chart",
            f"Monthly Savings ({period_label})",
            help_text,
        )
        canvas = FigureCanvasQTAgg(fig)
        window.set_canvas(canvas)
        canvas.draw()
        window.show()
        window.raise_()
        window.activateWindow()

    def show_expense_pie_chart(self):
        monthly_expenses = self.current_month_transactions("expense")
        if not monthly_expenses:
            QMessageBox.information(self, "No expenses recorded", "Log some expenses to view the pie chart.")
            return
        if not MATPLOTLIB_AVAILABLE or Figure is None or FigureCanvasQTAgg is None:
            QMessageBox.warning(
                self,
                "Visualization unavailable",
                "matplotlib is required to render charts.\nInstall it by typing this into the terminal: pip install matplotlib",
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

        year, month = self._selected_period()
        period_label = date(year, month, 1).strftime("%B %Y")
        dark_mode = getattr(self, "theme_mode", "dark") == "dark"
        text_color = "#E0E0E0" if dark_mode else "#212121"
        background_color = "#121212" if dark_mode else "#FFFFFF"
        panel_color = "#1C1C21" if dark_mode else "#FFFFFF"
        legend_face = "#1F1F26" if dark_mode else "#F2F2F2"
        legend_border = "#2E2E38" if dark_mode else "#D0D0D0"

        fig = Figure(figsize=(6, 4))
        fig.patch.set_facecolor(background_color)
        ax = fig.add_subplot(111)
        ax.set_facecolor(panel_color)
        try:
            import matplotlib
            cmap = matplotlib.colormaps["viridis"]
            colors = [cmap(i / len(values)) for i in range(len(values))]
        except Exception:
            colors = None
        wedges, texts = ax.pie(
            values,
            labels=None,
            autopct=None,
            startangle=90,
            colors=colors,
            textprops={"color": text_color},
            wedgeprops={"linewidth": 1.0, "edgecolor": background_color if dark_mode else "#FFFFFF"},
        )
        legend_labels = [f"{cat}: RM {val:.2f}" for cat, val in zip(categories, values, strict=False)]
        legend = ax.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            facecolor=legend_face,
            edgecolor=legend_border,
        )
        for text in legend.get_texts():
            text.set_color(text_color)
        legend.get_title().set_color(text_color)
        ax.axis("equal")
        ax.set_title(f"Monthly Expenses ({period_label})", color=text_color)
        fig.tight_layout()

        help_text = (
            "This chart shows the expense distribution for the current month. "
            "Amounts include every expense transaction recorded for the selected period. "
            "Refer to the legend on the right for category totals."
        )
        window = self._get_chart_window(
            "expense_pie_chart",
            f"Monthly Expenses ({period_label})",
            help_text,
        )
        canvas = FigureCanvasQTAgg(fig)
        window.set_canvas(canvas)
        canvas.draw()
        window.show()
        window.raise_()
        window.activateWindow()


    def submit_default_transaction(self):
        self.handle_add_tx(self.last_tx_type)

    def handle_add_tx(self, ttype: str):
        self.last_tx_type = ttype
        self.add_tx(ttype)

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
        self.undo_stack.append(("transaction", txid))
        self.undo_stack = self.undo_stack[-20:]

        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.clear_inputs()

        if ttype == "expense":
            budget = self.budget_map.get(raw_category)
            if budget:
                spent = self.category_monthly_expense_total(raw_category)
                if spent > budget:
                    over = spent - budget
                    QMessageBox.warning(
                        self,
                        "Budget exceeded",
                        f"You have exceeded the {raw_category} budget by RM {over:.2f} this month.",
                    )
        self.toast(f"{ttype.capitalize()} added.")

    def update_balance(self):
        positive = self.balance >= 0
        arrow = "^" if positive else "v"
        fg = "#81C784" if positive else "#E57373"
        if self.theme_mode == "dark":
            bg = "#1E3A29" if positive else "#2A1515"
        else:
            bg = "#E8F5E9" if positive else "#FDE0DC"
        self.balance_label.setText(f"{arrow} Net Position: RM {self.balance:.2f}")
        self.balance_label.setStyleSheet(f"color: {fg}; background-color: {bg};")

    def undo_last_transaction(self):
        if not self.undo_stack:
            self.toast("Nothing to undo.", 3000)
            return
        action, txid = self.undo_stack.pop()
        if action != "transaction":
            self.toast("Nothing to undo.", 3000)
            return
        if not self._remove_transaction_by_id(txid):
            self.toast("Unable to undo last transaction.", 4000)
            return
        self.load_ledger()
        self.load_budgets()
        self.refresh_category_options()
        self.update_balance()
        self.update_summary()
        self.toast("Last transaction undone.", 4000)

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
        self.load_budgets()
        self.update_balance()
        self.update_summary()

    def apply_theme(self):
        if self.theme_mode == "dark":
            stylesheet = DARK_STYLESHEET
        else:
            stylesheet = LIGHT_STYLESHEET
        self.setStyleSheet(stylesheet)
        if self.converter_window is not None:
            self.converter_window.setStyleSheet(stylesheet)
        for window in list(self.chart_windows.values()):
            if window is None:
                continue
            window.setStyleSheet(stylesheet)
            window.apply_theme(self.theme_mode)
            self._apply_titlebar_palette(window)
        self.update_titlebar_theme()
        self._refresh_card_shadows()

    def _apply_titlebar_palette(self, widget: QWidget | None) -> None:
        if os.name != "nt" or widget is None:
            return
        try:
            hwnd = int(widget.winId())
            if hwnd == 0:
                return
            dwmapi = ctypes.windll.dwmapi
            dark_enabled = ctypes.c_int(1 if self.theme_mode == "dark" else 0)
            # Apply immersive dark mode flag for compatibility across Windows versions
            for attr in (19, 20):
                dwmapi.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(dark_enabled), ctypes.sizeof(dark_enabled))
            caption_color = ctypes.c_uint(0x00281D1D if self.theme_mode == "dark" else 0x00FFFFFF)
            text_color = ctypes.c_uint(0x00E0E0E0 if self.theme_mode == "dark" else 0x00212121)
            dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_color), ctypes.sizeof(caption_color))
            dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(text_color), ctypes.sizeof(text_color))
        except Exception:
            pass

    def update_titlebar_theme(self):
        self._apply_titlebar_palette(self)







if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set application-wide icon (affects taskbar/dock on many systems)
    try:
        app.setWindowIcon(get_app_icon())
    except Exception:
        pass
    win = BudgetTracker()
    win.show()
    sys.exit(app.exec_())

