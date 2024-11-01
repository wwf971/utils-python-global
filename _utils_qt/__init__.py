from __future__ import annotations # this line must be put at beginning of script

import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from typing import TYPE_CHECKING
from _utils_import import np, _utils_io, _utils_file
import math

from .system import (
    enable_system_scaling,
    disable_system_scaling,
    make_pyqt_draw_on_logical_screen_space,
    make_pyqt_draw_before_system_scaling,
    make_pyqt_draw_after_system_scaling
)

from .font import (
    get_font_size
)

from .size import (
    print_size,
    print_size_policy,
    print_size_policy_and_alignment,
    set_size_policy_vertical,
    set_size_policy_horizontal,
    str_to_size_policy,
    size_policy_to_str,
    set_size_hint,
    set_size_hint_height,
    set_size_hint_width,
    set_min_size_hint_width,
    set_min_size_hint_height,
)

from .alignment import (
    make_components_align_to_top,
    set_alignment_to_null,
    alignment_to_str,
    print_alignment,
)

from .widget_custom import (
    WidgetCustom,
    KeyValueH,
    WidgetDebug
)
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import (
    Qt, pyqtSignal
)
# from PyQt5.QtWidgets import QWidget # pip install PyQt5
from PyQt5 import (
    QtWidgets
)
from PyQt5.QtGui import (
    QIcon
)

from PyQt5.QtWidgets import (
    QWidget, QSplitter,
    QLabel, QApplication, QMainWindow
)


def print_pyqt_version():
    from PyQt5.QtCore import QT_VERSION_STR, PYQT_VERSION_STR
    print("Qt: v%s"%QT_VERSION_STR, "\tPyQt: v%s"%PYQT_VERSION_STR)

def np_array_to_QPixmap(NpArray: np.ndarray):
    height, width, ChannelNum = NpArray.shape
    ByteNumPerLine = 3 * width
    qImage = QtGui.QImage(
        NpArray.data,
        width, height,
        ByteNumPerLine,
        QtGui.QImage.Format_RGB888
    ) # PyQt5.QtGui.QImage
    qPixmap = QtGui.QPixmap.fromImage(qImage)
    return qPixmap # PyQt5.QtGui.QPixmap

def add_to_style_sheet(obj: QtWidgets.QWidget, styleSheetStr: str):
    # if not styleSheetStr.endswith(";"):
    #     styleSheetStr += ";"
    styleSheet = obj.styleSheet()
    obj.setStyleSheet(styleSheet + styleSheetStr)
    # Label1.setStyleSheet(styleSheet + "QLabel{background-color:rgb(0,0,255);color:red;}")
    return obj

def set_window_icon(widget, file_path_icon):
    # file_path_icon: can be .png file
    _utils_file.check_file_exist(file_path_icon)
    widget.setWindowIcon(QIcon(file_path_icon))

def make_label_text_selectable(label: QLabel):
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)

from PyQt5.QtCore import QProcess
def open_dir_in_explorer(dir_path):
    if not _utils_file.dir_exist(dir_path):
        print("dir_path not exist: %s"%dir_path)
        return
    # check the operating system and execute the corresponding command
    if os.name == 'nt':  # windows
        dir_path = _utils_file.dir_path_to_win_style(dir_path, trailing_slash=False)
        print("dir_path: %s"%dir_path)
        QProcess.startDetached('explorer.exe', [dir_path])
            # .exe后缀不可缺
    elif os.name == 'posix':  # Unix-like (Linux, macOS)
        dir_path = _utils_file.dir_path_to_unix_style(dir_path, trailing_slash=False)
        QProcess.startDetached('open', [dir_path])  # For macOS
        # for Linux, you might want to use 'xdg-open'
        # QProcess.startDetached('xdg-open', [folder_path])
    else:
        raise Exception

def set_fixed_height_for_layout_component(layout, height: int):
    # Set a fixed height for each widget in the layout
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()  # Get the widget at index i
        if widget:  # Ensure the widget exists
            widget.setFixedHeight(height)  # Set the desired fixed height

def make_splitter_not_collapsible(splitter: QSplitter):
    for index in range(splitter.count()):
        splitter.setCollapsible(index, False)