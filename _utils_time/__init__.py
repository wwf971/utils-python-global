import time
import math

import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import datetime
    from dateutil import tz
else:
    datetime = _utils_import.LazyImport("datetime")
    tz = _utils_import.LazyFromImport("dateutil", "tz")
    timezone = _utils_import.LazyFromImport("datetime", "timezone")

from .timer import Timer, Pauser
from .datetime import (
    datetime_obj_to_time_str,
    get_local_timezone,
    datetime_obj_change_timezone
)
from .unix import (
    get_unix_stamp_base_datetime_obj,
    unix_stamp_to_datetime_obj,
    get_current_unix_stamp,
    get_current_unix_stamp_int,
)