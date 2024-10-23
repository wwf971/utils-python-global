import os
import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import win32con
    import win32api
else:
    win32con = _utils_import.lazy_import("win32con")
    win32api = _utils_import.lazy_import("win32api")

from PyQt5 import QtWidgets, QtGui, QtCore

def enable_system_scaling():
    # This method should be called before QtWidgets.QApplication().
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" # use system DPI.

def disable_system_scaling():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0" # do not use system-level scale
    # app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

def make_pyqt_draw_after_system_scaling():
    """
    make pyqt draw shapes on screen space after system-level resolution scaling.
    Situation when drawing on screen space before/after system-level scaling have different behavior:
        - Change of window, shape and font size when dragging window across screen with different system-level scaling ratio
    """
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" # enable system-level resolution scaling
    # os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0" # avoid system-level resolution scaling
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        # Qt API will draw based on coords after system-level resolution scaling
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
make_pyqt_draw_on_logical_screen_space = make_pyqt_draw_after_system_scaling

def make_pyqt_draw_before_system_scaling():
    """
    make pyqt draw shapes on screen space after system-level resolution scaling.
    Situation when drawing on screen space before/after system-level scaling have different behavior:
        - Change of window, shape and font size when dragging window across screen with different system-level scaling ratio
    """
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0" # avoid system-level resolution scaling
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        # Qt API will draw based on coords after system-level resolution scaling
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)