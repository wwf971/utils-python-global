from _utils_import import plt, np
import math


def set_yticks_int(ax: plt.Axes, min, max, Method="Auto", **Dict):
    if min > max:
        min, max = max, min
    #min, max = round(min) + 1, round(max)
    Ticks, TicksStr = calc_ticks_int(Method, min, max, **Dict)
    ax.set_yticks(Ticks, labels=TicksStr)
    #ax.set_yticklabels(TicksStr)
    return Ticks, TicksStr


def calc_ticks_int(Method="Auto", min=None, max=None, **Dict):
    assert isinstance(min, int) and isinstance(max, int)
    if Method in ["Auto", "auto"]:
        Range = max - min
        Interval = CalculateTickIntervalInt(min, max)
        Ticks = []
        Ticks.append(min)
        Tick = round(math.ceil(1.0 * min / Interval) * Interval)
        if Tick - min < 0.1 * Interval:
            pass
        else:
            Ticks.append(Tick)
        while Tick < max:
            Tick += Interval
            if max - Tick < 0.1 * Interval:
                break
            else:
                Ticks.append(Tick)
        Ticks.append(max)
    elif Method in ["Linear"]:
        Num = Dict["Num"]
        Ticks = np.rint(np.linspace(min, max, num=Num))
    else:
        raise Exception()

    TicksStr = list(map(lambda tick:str(int(tick)), Ticks))
    Offset = Dict.setdefault("Offset", 0.0)
    if Offset != 0.0:
        Ticks = list(map(lambda tick:tick + Offset, Ticks))
    return Ticks, TicksStr


def CalculateTickIntervalInt(min, max):
    Range = max - min
    if Range <= 0:
        return 1
    elif Range <= 5:
        return 2

    Log = round(math.log(Range, 10))
    base = 1.0
    Interval = base * 10 ** Log
    tick_num = Range / Interval

    while not 2.5 <= tick_num <= 6.5:
        if tick_num > 6.0:
            base, Log = next_interval_up(base, Log)
        elif tick_num < 3.0:
            base, Log = next_interval_down(base, Log)
        else:
            break
        Interval = base * 10 ** Log
        tick_num = Range / Interval
    return round(Interval)

def next_interval_up(base, Log):
    if base == 1.0:
        base = 2.0
    elif base == 2.0:
        base = 5.0
    elif base == 5.0:
        base = 1.0
        Log += 1
    else:
        raise Exception()
    return base, Log

def next_interval_down(base, Log):
    if base == 1.0:
        base = 5.0
        Log -= 1
    elif base == 2.0:
        base = 1.0
    elif base == 5.0:
        base = 2.0
    else:
        raise Exception()
    return base, Log