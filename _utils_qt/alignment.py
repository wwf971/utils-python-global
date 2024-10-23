from __future__ import annotations
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout
)
from PyQt5 import QtCore
def make_components_align_to_top(layout: QVBoxLayout):
    layout.setAlignment(QtCore.Qt.AlignTop)
