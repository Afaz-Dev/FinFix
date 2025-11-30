from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import (
    QColor,
    QFont,
    QIcon,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QBrush,
)


def _generate_logo_pixmap(size: int = 128) -> QPixmap:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    try:
        p.setRenderHint(QPainter.Antialiasing, True)

        # Background: rounded circle with vertical gradient
        grad = QLinearGradient(0, 0, 0, size)
        grad.setColorAt(0.0, QColor("#3F51B5"))  # Indigo 500
        grad.setColorAt(1.0, QColor("#2196F3"))  # Blue 500
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        margin = size * 0.06
        rect = QRectF(margin, margin, size - 2 * margin, size - 2 * margin)
        p.drawEllipse(rect)

        # Foreground: "FF" text (FinFix) centered
        p.setPen(QPen(QColor("#FFFFFF")))
        font = QFont("Segoe UI", int(size * 0.34))
        font.setWeight(QFont.DemiBold)
        p.setFont(font)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "FF")
    finally:
        p.end()
    return pix


def _load_user_logo_png(size: int) -> QPixmap | None:
    base = Path(__file__).resolve().parent
    candidate = base / "assets" / "logo.png"
    if not candidate.exists():
        return None
    pm = QPixmap()
    if pm.load(str(candidate)):
        if size > 0:
            pm = pm.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        return pm
    return None


def get_logo_pixmap(size: int = 96) -> QPixmap:
    # Prefer user-provided assets/logo.png if available; otherwise generate a default.
    user = _load_user_logo_png(size)
    return user if user is not None else _generate_logo_pixmap(size)


def get_app_icon(size: int = 256) -> QIcon:
    return QIcon(get_logo_pixmap(size))
