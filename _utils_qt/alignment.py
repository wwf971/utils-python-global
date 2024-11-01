from __future__ import annotations
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout
)
from PyQt5 import QtWidgets, QtCore
from _utils_import import _utils_io

def make_components_align_to_top(layout: QVBoxLayout):
    layout.setAlignment(QtCore.Qt.AlignTop)

def set_alignment_to_null(Obj: QtWidgets.QLayout):
    Obj.setAlignment(QtCore.Qt.Alignment()) # alignment_to_str(Obj) will return null


def alignment_to_str(Alignment: QtCore.Qt.AlignmentFlag) -> str:
    """
    test
        alignment_to_str(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter) -> AlignCenter|AlignVCenter
        alignment_to_str(QtCore.Qt.Alignment()) -> null
    """
    AlignmentInt = int(Alignment)
    
    TypeListHorizontal = []
    TypeListVertical = []
    if AlignmentInt // 128 == 1:
        TypeListVertical.append("AlignVCenter")
        AlignmentInt = AlignmentInt % 128
    if AlignmentInt // 64 == 1:
        TypeListVertical.append("AlignBottom")
        AlignmentInt = AlignmentInt % 64
    if AlignmentInt // 32 == 1:
        TypeListVertical.append("AlignTop")
        AlignmentInt = AlignmentInt % 32
    AlignmentInt = AlignmentInt % 8
    if AlignmentInt // 4 == 1:
        TypeListHorizontal.append("AlignHCenter")
        AlignmentInt = AlignmentInt % 4
    if AlignmentInt // 2 == 1:
        TypeListHorizontal.append("AlignRight")
        AlignmentInt = AlignmentInt % 2
    if AlignmentInt // 1 == 1:
        TypeListHorizontal.append("AlignLeft")
        AlignmentInt = AlignmentInt % 1

    if isinstance(Alignment, QtWidgets.QWidget):
        pass

    if len(TypeListHorizontal) > 0:
        align_horizontal = "|".join(TypeListHorizontal)
    else:
        align_horizontal = "null"

    if len(TypeListVertical) > 0:
        align_vertical = "|".join(TypeListVertical)
    else:
        align_vertical = "null"

    return align_horizontal, align_vertical

def print_alignment(Widget, widget_name=None, pipe_out=None):
    """
    test
        print_alignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    """
    if pipe_out is None:
        pipe_out = _utils_io.PipeOut()
    if widget_name is None:
        widget_name = "Window"
    if widget_name == "":
        pipe_out.print("alignment:")
    else:
        pipe_out.print("%s. alignment:"%widget_name)
    if hasattr(Widget, "alignment"):
        align_horizontal, align_vertical = alignment_to_str(Widget.alignment())
        with pipe_out.increased_indent():
            pipe_out.print("Horizontal: %s"%align_horizontal)
            pipe_out.print("Vertical  : %s"%align_vertical)
    else:
        pipe_out.print("method not supported.")