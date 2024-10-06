

import _utils_file
import re
def move_if_file_name_match_pattern(
    dir_path,
    dir_path_target,
    pattern=None,
):
    pattern_compiled = re.compile(pattern)
    dir_path_target = _utils_file.dir_path_to_unix_style(dir_path)
    for file_name in _utils_file.list_all_file_name(dir_path):
        if pattern_compiled.match(file_name) is not None:
            _utils_file.move_file(dir_path, dir_path_target + file_name)