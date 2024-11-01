from _utils_import import _utils_io
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy
)
from PyQt5.QtCore import (
    QSize
)

def print_size_policy_and_alignment(widget: QtWidgets.QWidget, widget_name="Window", pipe_out = None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    pipe_out.print("%s. size and alignment:"%widget_name)
    with pipe_out.increased_indent():
        print_alignment(widget, widget_name="", pipe_out=pipe_out)
        print_size_policy(widget, widget_name="", pipe_out=pipe_out)
        print_size(widget, widget_name=None, pipe_out=pipe_out)

def print_size(widget: QtWidgets.QWidget, widget_name="Window", pipe_out = None):
    if pipe_out is None:
        pipe_out = _utils_io.PipeOut()
    if widget_name is not None:
        pipe_out.print("%s. size:"%widget_name)
    else:
        pipe_out.print("size:")
    with pipe_out.increased_indent():
        pipe_out.print("minWH:(%d, %d)"%(widget.minimumSize().width(), widget.minimumSize().height()))

        if hasattr(widget, "minimumSizeHint"):
            pipe_out.print("minSizeHintWH:(%d, %d)"%(widget.minimumSizeHint().width(), widget.minimumSizeHint().height()))
        else:
            pipe_out.print("minSizeHintWH: method not supported.")
        pipe_out.print("sizeHintWH:(%d, %d)"%(widget.sizeHint().width(), widget.sizeHint().height()))
        if hasattr(widget, "sizePolicy"):
            pipe_out.print("SizePolicyHorizontal: %s"%size_policy_to_str(widget.sizePolicy().horizontalPolicy()))
            pipe_out.print("SizePolicyVertical  : %s"%size_policy_to_str(widget.sizePolicy().verticalPolicy()))
        else:
            pipe_out.print("SizePolicy: method not supported.")

def size_policy_to_str(size_policy: QSizePolicy.Policy):
    GrowFlag = size_policy & QSizePolicy.GrowFlag # 1
    ExpandFlag = size_policy & QSizePolicy.ExpandFlag # 2
    ShrinkFlag = size_policy & QSizePolicy.ShrinkFlag # 4
    IgnoreFlag = size_policy & QSizePolicy.IgnoreFlag # 8
    
    FlagList = []
    if GrowFlag:
        FlagList.append("GrowFlag")
    if ExpandFlag:
        FlagList.append("ExpandFlag")
    if ShrinkFlag:
        FlagList.append("ShrinkFlag")
    if IgnoreFlag:
        FlagList.append("IgnoreFlag")
    
    if len(FlagList) == 0:
        FlagList = ["NoFlag"]

    if size_policy == QSizePolicy.Fixed:
        size_policy_str = "Fixed" # 0
    elif size_policy == QSizePolicy.Minimum:
        size_policy_str = "Minimum" # 1
    elif size_policy == QSizePolicy.MinimumExpanding:
        size_policy_str = "MinimumExpanding" # 3
    elif size_policy == QSizePolicy.Maximum:
        size_policy_str = "Maximum" # 4
    elif size_policy == QSizePolicy.Preferred:
        size_policy_str = "Preferred" # 5
    elif size_policy == QSizePolicy.Expanding:
        size_policy_str = "Expanding" # 7
    elif size_policy == QSizePolicy.Ignored:
        size_policy_str = "Ignored" # 13
    else:
        size_policy_str = "NoName"
    return "%s(%s)"%(size_policy_str, "|".join(FlagList))

def str_to_size_policy(size_policy_str: str):
    size_policy_str = size_policy_str.lower()
    if size_policy_str in ["fixed"]: # 0
        size_policy = QSizePolicy.Fixed
    elif size_policy_str in ["minimum"]: # 1
        size_policy = QSizePolicy.Minimum
    elif size_policy_str in ["minimumexpanding"]: # 3
        size_policy = QSizePolicy.MinimumExpanding
    elif size_policy_str in ["maximum"]: # 4
        size_policy = QSizePolicy.Maximum
    elif size_policy_str in ["preferred"]: # 5
        size_policy = QSizePolicy.Preferred
    elif size_policy_str in ["expanding"]: # 7
        size_policy = QSizePolicy.Expanding    
    elif size_policy_str in ["ignored"]: # 13
        size_policy = QSizePolicy.Ignored    
    else:
        raise NotImplementedError
    size_policy_str = size_policy_str.lower()
    return size_policy

def set_size_policy_vertical(widget: QWidget, size_policy: str):
    if isinstance(size_policy, str):
        size_policy = str_to_size_policy(size_policy)
    # get the current size policy
    _size_policy = widget.sizePolicy()

    # set only the horizontal policy to expanding, keeping vertical policy unchanged
    _size_policy.setVerticalPolicy(size_policy)

    # apply the modified size policy back to the widget
    widget.setSizePolicy(_size_policy)

def set_size_policy_horizontal(widget: QWidget, size_policy: str):
    if isinstance(size_policy, str):
        size_policy = str_to_size_policy(size_policy)
    # get the current size policy
    _size_policy = widget.sizePolicy()

    # set only the horizontal policy to expanding, keeping vertical policy unchanged
    _size_policy.setHorizontalPolicy(size_policy)

    # apply the modified size policy back to the widget
    widget.setSizePolicy(_size_policy)

def print_size_policy(widget: QWidget, widget_name=None, pipe_out=None):
    if pipe_out is None:
        pipe_out = _utils_io.PipeOut()
    if widget_name is None:
        widget_name = "Window"
    if widget_name == "":
        pipe_out.print("sizePolicy:")
    else:
        pipe_out.print("%s. sizePolicy:"%widget_name)
    if hasattr(widget, "sizePolicy"):
        SizePolicy = widget.sizePolicy()
        with pipe_out.increased_indent():
            pipe_out.print("Horizontal: %s"%size_policy_to_str(SizePolicy.horizontalPolicy()))
            pipe_out.print("Vertical  : %s"%size_policy_to_str(SizePolicy.verticalPolicy()))
    else:
        with pipe_out.increased_indent():
            pipe_out.print("method not supported")
    return

def set_size_hint(widget: QWidget, width, height):
    widget.sizeHint = lambda: QSize(width, height)

def set_size_hint_width(widget: QWidget, width):
    height = widget.sizeHint().height()
    widget.sizeHint = lambda: QSize(width, height)

def set_size_hint_height(widget: QWidget, height):
    width = widget.sizeHint().width()
    widget.sizeHint = lambda: QSize(width, height)


def set_min_size_hint_width(widget: QWidget, width):
    height = widget.minimumSizeHint().height()
    widget.minimumSizeHint = lambda: QSize(width, height)

def set_min_size_hint_height(widget: QWidget, height):
    width = widget.minimumSizeHint().width()
    widget.minimumSizeHint = lambda: QSize(width, height)