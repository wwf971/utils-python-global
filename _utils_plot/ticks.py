from _utils_import import plt, np
import math


def set_yticks_int(ax: plt.Axes, min, max, method="Auto", **Dict):
    if min > max:
        min, max = max, min
    #min, max = round(min) + 1, round(max)
    ticks, ticks_str = calc_ticks_int(method, min, max, **Dict)
    ax.set_yticks(ticks, labels=ticks_str)
    #ax.set_yticklabels(ticks_str)
    return ticks, ticks_str

def set_xticks_int(ax: plt.Axes, min, max, method="Auto", **Dict):
    if min > max:
        min, max = max, min
    #min, max = round(min) + 1, round(max)
    ticks, ticks_str = calc_ticks_int(method, min, max, **Dict)
    ax.set_xticks(ticks, labels=ticks_str)
    #ax.set_yticklabels(ticks_str)
    return ticks, ticks_str

def calc_ticks_int(method="Auto", min=None, max=None, **Dict):
    assert isinstance(min, int) and isinstance(max, int)
    if method in ["Auto", "auto"]:
        _range = max - min
        interval = calc_tick_interval_int(min, max)
        ticks = []
        ticks.append(min)
        Tick = round(math.ceil(1.0 * min / interval) * interval)
        if Tick - min < 0.1 * interval:
            pass
        else:
            ticks.append(Tick)
        while Tick < max:
            Tick += interval
            if max - Tick < 0.1 * interval:
                break
            else:
                ticks.append(Tick)
        ticks.append(max)
    elif method in ["Linear"]:
        Num = Dict["Num"]
        ticks = np.rint(np.linspace(min, max, num=Num))
    else:
        raise Exception()

    ticks_str = list(map(lambda tick:str(int(tick)), ticks))
    Offset = Dict.setdefault("Offset", 0.0)
    if Offset != 0.0:
        ticks = list(map(lambda tick:tick + Offset, ticks))
    return ticks, ticks_str

def calc_tick_interval_int(min, max):
    _range = max - min
    if _range <= 0:
        return 1
    elif _range <= 5:
        return 2

    log = round(math.log(_range, 10))
    base = 1.0
    interval = base * 10 ** log
    tick_num = _range / interval

    while not 2.5 <= tick_num <= 6.5:
        if tick_num > 6.0:
            base, log = next_interval_up(base, log)
        elif tick_num < 3.0:
            base, log = next_interval_down(base, log)
        else:
            break
        interval = base * 10 ** log
        tick_num = _range / interval
    return round(interval)

def set_xticks_float(ax, min, max, method="Auto", Rotate45=False):
    if not np.isfinite(min) or not np.isfinite(max):
        min, max = -5.0, 5.0
    if min == max:
        if min == 0.0:
            min, max = -1.0, 1.0
        elif min > 0.0:
            min, max = 0.5 * min, 1.5 * max
        else:  
            min, max = - 0.5 * min, - 1.5 * max

    ticks, ticks_str = calc_ticks_float(method, min, max)
    ticks, ticks_str = calc_ticks_float(method, min, max)
    ax.set_xticks(ticks)
    ax.set_xticklabels(ticks_str)

    if Rotate45: # Avoid Label overlapping
        plt.setp(
            ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor"
        )
    return ticks, ticks_str

def set_yticks_float(ax, min, max, method="Auto"):
    if not np.isfinite(min) or not np.isfinite(max):
        min, max = -5.0, 5.0
    if min == max:
        if min == 0.0:
            min, max = -1.0, 1.0
        else:
            min, max = 0.5 * min, 1.5 * max
    ticks, ticks_str = calc_ticks_float(method, min, max)
    ax.set_yticks(ticks)
    ax.set_yticklabels(ticks_str)
    return ticks, ticks_str

def calc_ticks_float(method="Auto", min=None, max=None, **kw):
    if method in ["Auto", "auto"]:
        Range = max - min
        interval, base, Log = CalculateTickintervalFloat(min, max)
        ticks = []
        ticks.append(min)
        Tick = math.ceil(min / interval) * interval
        if Tick - min < 0.1 * interval:
            pass
        else:
            ticks.append(Tick)
        while Tick < max:
            Tick += interval
            if max - Tick < 0.1 * interval:
                break
            else:
                ticks.append(Tick)
        ticks.append(max)
    elif method in ["Linear"]:
        Num = kw["Num"]
        ticks = np.linspace(min, max, num=Num)
    else:
        raise Exception()

    ticks_str = []
    if 1 <= Log <= 2:
        ticks_str = list(map(lambda tick:str(int(tick)), ticks))
    elif Log == 0:
        ticks_str = list(map(lambda tick:'%.1f'%tick, ticks))
    elif Log == -1:
        ticks_str = list(map(lambda tick:'%.2f'%tick, ticks))
    elif Log == -2:
        ticks_str = list(map(lambda tick:'%.3f'%tick, ticks))
    else:
        ticks_str = list(map(lambda tick:'%.2e'%tick, ticks))
    return ticks, ticks_str

def CalculateTickintervalFloat(min, max):
    Range = max - min
    if Range == 0.0:
        return 0.0, None, None

    Log = round(math.log(Range, 10))
    base = 1.0
    interval = base * 10 ** Log
    tick_num = Range / interval

    while not 2.5 <= tick_num <= 6.5:
        if tick_num > 6.0:
            base, Log = next_interval_up(base, Log)
        elif tick_num < 3.0:
            base, Log = next_interval_down(base, Log)
        else:
            break
        interval = base * 10 ** Log
        tick_num = Range / interval
    return interval, base, Log

def next_interval_up(base, log):
    if base == 1.0:
        base = 2.0
    elif base == 2.0:
        base = 5.0
    elif base == 5.0:
        base = 1.0
        log += 1
    else:
        raise Exception()
    return base, log

def next_interval_down(base, log):
    if base == 1.0:
        base = 5.0
        log -= 1
    elif base == 2.0:
        base = 1.0
    elif base == 5.0:
        base = 2.0
    else:
        raise Exception()
    return base, log


