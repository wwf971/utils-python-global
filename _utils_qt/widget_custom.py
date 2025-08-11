import _utils_qt
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow
import math

class WidgetCustom(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # size returned on self.minimumSizeHint()
        self.min_size_hint_width = -1
        self.min_size_hint_height = -1

        self.size_hint_width = -1
        self.size_hint_height = -1
    def get_style_sheet(self):
        return self.styleSheet()
    def add_to_style_sheet(self, style_sheet_str: str):
        # styleSheet = self.styleSheet()
        # self.setStyleSheet(styleSheet + style_sheet_str)
        self.setStyleSheet(self.styleSheet() + style_sheet_str)
        return self
    def set_min_size(self, width, height):
        """
        set minimum width and height of client area.
            does not include title bar.
        """
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        return self
    def get_min_size(self):
        """
        can be set by QWidget.setMinimumSize(width, height)
            or QWidget.setMinimumWidth(width) and QWidget.setMinimumheight(height)
        """
        min_size = self.minimumSize()
        return min_size.width(), min_size.height()
        # return self.minimumHeight(), self.minimumWidth()
    def set_min_size_hint(self, width, height):
        # if not set, will return QSize(-1, -1)
        self.min_size_hint_width = width
        self.min_size_hint_height = height
    def minimumSizeHint(self):
        """
        QWidget.minimumSizeHint returns QSize(-1, -1).
            this means QWidget does not specify a minimum default size.
        """
        return QtCore.QSize(
            self.min_size_hint_width, # width
            self.min_size_hint_height # height
        )
    def set_size_hint(self, width, height):
        self.size_hint_width = width
        self.size_hint_height = height
        return
    def sizeHint(self) -> QtCore.QSize:
        """
        returns (-1, -1) if there is no width or height
        """
        return QtCore.QSize(self.size_hint_width, self.size_hint_height)


    set_min_window_size = set_min_size
    def set_size(self, width, height):
        # self.setFixedSize(width, height)
        # self.setMinimumSize(0, 0)
        # self.setMaximumSize(65536, 65536)
        self.resize(width, height)
        return self
    set_window_size = set_size
    def set_window_pos(self, x_left, y_top):
        self.move(x_left, y_top)
        return self
    def set_window_pos_and_size(self, x_left, y_top, width, height):
        self.setGeometry(x_left, y_top, width, height) # x_left, y_top, width, height
        return self
    def get_size_policy(self):
        return self.sizePolicy()
    def get_cursor_xy_global():
        """
        return cursor coord in global screen space
        if environment variable 
        """
        pos = QtGui.QCursor.pos()
        return pos.x(), pos.y()
    def get_system_level_screen_scale(self):
        """
        获取当前显示器的系统层面分辨率缩放系数(ratio of system-level resolution scaling).
        举例
            分辨率3840x2160的显示器, 在175%系统层面分辨率缩放后, 分辨率将变为2914 x 1234.
        """
        # self.LabelScreenInfo3.setText("scaling: %.2f %.2f"%(self.logicalDpiX(), self.logicalDpiY()))
        # self.LabelScreenInfo3.setText("scaling: %.2f"%(self.window().screen().logicalDotsPerInch()))
        # self.LabelScreenInfo3.setText("scaling: %.2f"%self.physicalDpiX())
        
        # ratioInt = self.window().devicePixelRatio() # -> int
        ratioFloat = self.window().devicePixelRatioF() # -> float
            # bug. 有些情况下存在. 数值被rounded. 如实际缩放率为1.75, 但是该方法返回2.00.
        return ratioFloat

class KeyValueH(QtWidgets.QHBoxLayout):
    def __init__(self, key, value, width1, width2, height, spacing):
        super().__init__()

        label1 = QtWidgets.QLabel(key)
        label1.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        label1.sizeHint = lambda:QtCore.QSize(width1, height)
        label1.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # label1.setFixedSize()可以完成类似的工作

        label2 = QtWidgets.QLabel(value)
        label2.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        label2.sizeHint = lambda:QtCore.QSize(width2, height)
        label2.setMaximumSize(width2 * 2, height)
        label2.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)

        self.addWidget(label1)
        self.addWidget(label2)

        self.label1, self.label2 = label1, label2
        self._spacing = spacing

    def getMaximumWidth(self):
        return self.label1.sizeHint().width() + self.label2.maximumWidth() + 3 * self._spacing


class WidgetDebug(
    WidgetCustom
):
    """封装了一系列设定窗口/组件属性的一系列相关函数."""
    def __init__(self,
        # background_color=(200, 200, 200, 127), # RGB
        background_color=(255, 255, 255, 127),
        border_color=None, # RGB
        border_width=1,
        draw_grid=False,
        margin=0,
    ):
        super().__init__()
        self.setMouseTracking(True) # trigger mouseMoveEvent
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
            # if not set this attribute, background-color of this widget will not render.

        # self.show()
        # self.setStyleSheet( # 可能导致滚动条问题
        #     "background-color: rgba(%d, %d, %d, %d); "%(
        #         background_color[0],
        #         background_color[1],
        #         background_color[2],
        #         255 if len(background_color) <= 3 else background_color[3]
        #     )
        # )
        # self.setStyleSheet("background-color: red;")

        # self.add_to_style_sheet(
        #     "margin: %dpx;"%Margin
        # )
        if border_color is None:
            border_color = (0, 0, 0, 255)
        self.border_color = border_color
        self.border_width = border_width
        self.set_border_prop(self.border_color, self.border_width)
        # use for a container widget
        # self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Plain)
            # QWidget does not have this method. only QFrame has this method.
        # self.setLinewidth(1)

        self.draw_grid = draw_grid
    # def setCentralWidget(self, widget):
    #     QMainWindow.setCentralWidget(self, widget)
    #     return self
    def set_border_prop(self, border_color, border_width):
        # set border color
        self.add_to_style_sheet(
            "WidgetDebug{ border-color: rgba(%d, %d, %d, %d); }"%(
                border_color[0], border_color[1], border_color[2],
                255 if len(border_color) <= 3 else border_color[3],
            )
        ) # only apply to this instance
        # set border width
        self.add_to_style_sheet(
            "WidgetDebug{ border-width: %dpx; border-style: solid; }"%(
                border_width
            )
        ) # only apply to this instance
    def set_window_title(self, Title):
        self.WindowTitle = Title
        self.setWindowTitle(Title)
        return self
    def DefaultwidthheightStepOnResize(self):
        """
        step length when changing width and height of window, during resizing events.
        default: (0, 0)
        """
        DefaultSize = self.sizeIncrement()
        return DefaultSize.width(), DefaultSize.height()
    def add_label(
        self, name, 
        x_left, y_top, width, height,
        Str: str=None,
        AllowMultiLine=True,
        FontColor=None,
        background_color=None
    ):
        label = QtWidgets.QLabel(self)
        label.setGeometry(x_left, y_top, width, height)
        if Str is not None:
            label.setText(Str)
        setattr(self, name, label)
        if AllowMultiLine:
            label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        if background_color is not None:
            if len(background_color) == 3: # RGB, uint with range [0, 255].
                label.setStyleSheet("background-color: (%d, %d, %d)"%(background_color[0], background_color[1], background_color[2]))
            else:
                raise NotImplementedError()
        return self
    def set_full_screen(self):
        self.cancel_fixed_size()
        WindowFlags = self.windowFlags()
        self.setWindowFlags(WindowFlags | QtCore.Qt.Window) # full screen window must top-level window.
        self.showFullScreen()
        # self.setWindowState(QtCore.Qt.WindowFullScreen)
    def cancel_full_screen(self):
        WindowFlags = self.windowFlags()
        self.setWindowFlags(WindowFlags & QtCore.Qt.SubWindow) # full screen window must top-level window.
        self.showNormal()
    def paintEvent(self, event):
        if self.draw_grid:
            self.draw_grid_on_background()
        self.draw_border()
    def draw_grid_on_background(self, point_interval=100):
        # draw point grid. for debug.
        width, height = self.get_width_height()
        row_num = math.ceil(height / point_interval)
        for col_index in range(math.ceil(width / point_interval)):
            for row_index in range(row_num):
                self.draw_point(
                    point_interval * col_index, point_interval * row_index,
                    Color=(255, 0, 0, 100),
                    width=5
                )
        return self
    def set_always_on_top(self):
        # make this window always on top of other windows
        window_flags = self.windowFlags()
        self.setWindowFlags(window_flags | QtCore.Qt.WindowStaysOnTopHint)
        return self
    def toggle_always_on_top(self):
        if self.is_always_on_top():
            self.cancel_always_on_top()
        else:
            self.set_always_on_top()
        return self
    def cancel_always_on_top(self):
        WindowFlags = self.windowFlags()
        self.setWindowFlags(WindowFlags & ~QtCore.Qt.WindowStaysOnTopHint) # WindowStaysOnTopHint: window always on top.
        self.show() # show window again after changing window flags
    def is_always_on_top(self):
        WindowFlags = self.windowFlags()
        return WindowFlags & QtCore.Qt.WindowStaysOnTopHint
    def cancel_always_on_top(self):
        windowFlags = self.windowFlags()
        self.setWindowFlags(windowFlags & ~QtCore.Qt.WindowStaysOnTopHint)
        return self
    def set_pos(self, x_left, y_top):
        self.move(x_left, y_top)
    set_window_pos = set_pos
    def set_fixed_size(self, width=None, height=None):
        # make it unable to resize by draggin edge of window
        if width is None or height is None:
            width, height = self.get_width_height()
        self.setFixedSize(width, height)
    def get_width_height(self):
        Rect = self.geometry()
        width = Rect.width()
        height = Rect.height()
        return width, height
    def set_width_height(self, width, height):
        self.resize(width, height)
        return self
    def cancel_fixed_size(self):
        # make window can be resized by dragging at edge of window
        self.setMinimumSize(0, 0)
        self.setMaximumSize(65536, 65536)
    allow_resize = cancel_fixed_size
    def set_no_frame(self):
        windowFlags = self.windowFlags()
        self.setWindowFlags(windowFlags | QtCore.Qt.FramelessWindowHint)
        return self
    def get_window_handle(self) -> int:
        """
        Windows system handle is an 32bit/64bit integer
        """
        hWindow = int(self.winId())
        return hWindow

    def draw_rect(
            self,
            x_left, y_top, width, height,
            background_color=(10, 10, 100, 40), # RGBA
            border_color=(0, 0, 0, 100), # RGBA
            border_width=1,
            Text=None
        ):
        Painter = QtGui.QPainter(self)
        if background_color is not None:
            Brush = QtGui.QBrush(QtGui.QColor(*background_color)) 
            Painter.setBrush(Brush) # internal color of rectangle
        if border_color is not None:
            # assert len(border_color) in [3, 4]
            Painter.setPen(
                QtGui.QPen(QtGui.QColor(*border_color), border_width)
            )
        Painter.drawRect( # draw a rectangle
            QtCore.QRect(
                QtCore.QPoint(round(x_left), round(y_top)), # XY coord of left top point
                QtCore.QPoint(round(x_left + width), round(y_top + height)) # XY coord of right bottom point
            )
        ) # drawXXX must be in paintEvent

        if Text is not None: # draw text in the rectangle
            self.draw_text(
                x_left, y_top, width, height, Text, FontScale=1.5
            )
    def draw_border(self, border_color=None):
        """
        draw border of this component, for debug
        """
        if border_color is None:
            border_color = self.border_color
        self.draw_rect(
            0, 0, self.width() -1, self.height() -1,
            background_color=None,
            border_color=border_color,
            border_width=1
        )

    def draw_text(self, 
            x_left, y_top, width, height, text,
            align_horizontal=None, align_vertical=QtCore.Qt.AlignVCenter,
            font_scale=1.0
        ):
        painter = QtGui.QPainter(self)
        # set texts alignment
        if align_horizontal is None:
            align_horizontal = QtCore.Qt.AlignCenter
        if align_vertical is None:
            align_vertical = QtCore.Qt.AlignVCenter

        # set text font size
        font = painter.font() # PyQt5.QtGui.QFont
        font.setPointSize(font.pointSize() * font_scale)
        painter.setFont(font)

        painter.drawText(
            QtCore.QRect(
                QtCore.QPoint(round(x_left), round(y_top)), # XY coord of left top point
                QtCore.QPoint(round(x_left + width), round(y_top + height)) # XY coord of right bottom point
            ),
            align_horizontal | align_vertical, # |Qt.AlignTop,
            text
        )
    def draw_point(
            self,
            X, Y,
            Color=(10, 10, 100, 80), # RGBA,
            width=10 # shape of point is actually square
        ):
        Painter = QtGui.QPainter(self)
        Pen = QtGui.QPen(QtGui.QColor(*Color))
        Pen.setWidth(width) # size of point to be drawn
            # point actually has rectangle shape
        Painter.setPen(Pen)
        Painter.drawPoint( # draw a rectangle
            QtCore.QPoint(round(X), round(Y)), # XY coord of point
        ) # drawXXX must be in paintEvent

class LabelCustom(QtWidgets.QLabel, WidgetCustom):
    def add_to_style_sheet(self, styleSheetStr: str):
        return _utils_qt.add_to_style_sheet(self, styleSheetStr)
    def set_font_color(self, color):
        _utils_qt.add_to_style_sheet(self, "color: %s;"%Color)
        return self
    def set_text_alignment(
        self,
        horizontal="Center",
        vertical="Center"
    ):
        # 设置水平对齐和垂直对齐.
        # 自身内部的文字/子widget在自身中的位置
        return self