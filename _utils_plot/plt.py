


import _utils_file
from _utils_import import plt
import math
from typing import TYPE_CHECKING
import _utils_import
if TYPE_CHECKING:
    import matplotlib as mpl
    # mpl.use('TkAgg',force=True)
    # ImportError: Cannot load backend 'TkAgg' which requires the 'tk' interactive framework, as 'headless' is currently running
    import matplotlib.pyplot as plt
    import matplotlib.image
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
else:
    mpl = _utils_import.lazy_import("matplotlib")
    # plt = _utils_import.lazy_from_import("matplotlib", "pyplot")
    plt = _utils_import.lazy_import("matplotlib.pyplot")
    Line2D = _utils_import.lazy_from_import("matplotlib.pyplot", "Line2D")
    Rectangle = _utils_import.lazy_from_import("matplotlib.patches", "Rectangle")
    image = _utils_import.lazy_import("matplotlib.image")

from .ticks import (
    set_yticks_int,
    calc_ticks_int,
)
from .scatter_with_dist import (
    plot_scatter_with_dist
)

def create_fig_plt(plot_num=1, row_num=None, col_num=None, width=None, height=None, size="Small"):
    row_num, col_num = parse_row_col_num(plot_num, row_num, col_num)
    if width is None and height is None:
        if size in ["Small", "S"]:
            ax_size = 5.0
        elif size in ["Medium", "M"]:
            ax_size = 7.5
        elif size in ["Large", "L"]:
            ax_size = 10.0
        else:
            raise Exception(size)
        width = col_num * ax_size # inches
        height = row_num * ax_size # inches
    elif width is not None and height is not None:
        pass
    else:
        raise Exception()
    plt.close()
    fig, axes = plt.subplots(nrows=row_num, ncols=col_num, figsize=(width, height))
    return fig, axes
CreateFigure = CreateCanvasPlt = create_fig_plt

def save_fig_for_plt(
    save=True, file_path_save=None,
    fig=None, tight_layout=True,
    remove_margin=True
):
    if file_path_save is not None:
        save = True
    if file_path_save is None and save is True:
        raise Exception()
    if save:
        if fig is not None:
            fig.savefig(file_path_save)
        else:
            file_path_save = _utils_file.create_dir_for_file_path(file_path_save)
            if tight_layout:
                plt.tight_layout()
            # plt.savefig(file_path_save, format="svg")
            if remove_margin:
                # plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
                # plt.margins(0, 0)
                plt.savefig(
                    file_path_save, 
                    bbox_inches = 'tight',
                    pad_inches = 0.25
                )
            else:
                plt.savefig(file_path_save)
            # plt.close() # is closed, plt.show() will not function normally.


def parse_row_col_num(plot_num, row_num=None, col_num=None):
    # print(row_num, col_num)
    # col_num: int. Column Number.
    if row_num in ["Auto", "auto"]:
        row_num = None
    if col_num in ["Auto", "auto"]:
        col_num = None
    if row_num is None:
        if col_num is None:
            if plot_num <= 3:
                return 1, plot_num
            col_num = round(plot_num ** 0.5)
            if col_num == 0:
                col_num = 1
            row_num = plot_num // col_num
            if plot_num % col_num > 0:
                row_num += 1
            return row_num, col_num
        else:
            row_num = plot_num // col_num
            if plot_num % col_num > 0:
                row_num += 1
            return row_num, col_num
    else:
        if col_num is None:
            col_num = plot_num // row_num
            if plot_num % row_num > 0:
                col_num += 1
            return row_num, col_num
        else:
            if plot_num != row_num * col_num:
                raise Exception('plot_num: %d != row_num %d x ColumnNum %d'%(plot_num, row_num, col_num))
            else:
                return row_num, col_num

def plot_line_plt(ax, PointStart, PointEnd, width=1.0, color=(0.0, 0.0, 0.0, 1.0), style="-"):
    # width: Line width in points(?pixels)
    X = [PointStart[0], PointEnd[0]]
    Y = [PointStart[1], PointEnd[1]]
    line = ax.add_line(Line2D(X, Y))
    line.set_linewidth(width)
    line.set_color(color)
    line.set_linestyle(style)
plot_line = plot_line_plt