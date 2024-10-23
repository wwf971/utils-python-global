from _utils_import import _utils_io
from PyQt5 import QtWidgets, QtCore, QtGui

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

def size_policy_to_str(SizePolicy: QtWidgets.QSizePolicy.Policy):
    GrowFlag = SizePolicy & QtWidgets.QSizePolicy.GrowFlag # 1
    ExpandFlag = SizePolicy & QtWidgets.QSizePolicy.ExpandFlag # 2
    ShrinkFlag = SizePolicy & QtWidgets.QSizePolicy.ShrinkFlag # 4
    IgnoreFlag = SizePolicy & QtWidgets.QSizePolicy.IgnoreFlag # 8
    
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

    if SizePolicy == QtWidgets.QSizePolicy.Fixed:
        Name = "Fixed" # 0
    elif SizePolicy == QtWidgets.QSizePolicy.Minimum:
        Name = "Minimum" # 1
    elif SizePolicy == QtWidgets.QSizePolicy.MinimumExpanding:
        Name = "Expanding" # 3
    elif SizePolicy == QtWidgets.QSizePolicy.Maximum:
        Name = "Maximum" # 4
    elif SizePolicy == QtWidgets.QSizePolicy.Preferred:
        Name = "Preferred" # 5
    elif SizePolicy == QtWidgets.QSizePolicy.Expanding:
        Name = "Expanding" # 7
    elif SizePolicy == QtWidgets.QSizePolicy.Ignored:
        Name = "Ignored" # 13
    else:
        Name = "NoName"
    return "%s(%s)"%(Name, "|".join(FlagList))

def print_size_policy(widget: QtWidgets.QWidget, widget_name=None, pipe_out=None):
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
        AlignmentHorizontal = "|".join(TypeListHorizontal)
    else:
        AlignmentHorizontal = "null"

    if len(TypeListVertical) > 0:
        AlignmentVertical = "|".join(TypeListVertical)
    else:
        AlignmentVertical = "null"

    return AlignmentHorizontal, AlignmentVertical

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
        AlignmentHorizontal, AlignmentVertical = alignment_to_str(Widget.alignment())
        with pipe_out.increased_indent():
            pipe_out.print("Horizontal: %s"%AlignmentHorizontal)
            pipe_out.print("Vertical  : %s"%AlignmentVertical)
    else:
        pipe_out.print("method not supported.")

def set_alignment_to_null(Obj: QtWidgets.QLayout):
    Obj.setAlignment(QtCore.Qt.Alignment()) # alignment_to_str(Obj) will return null