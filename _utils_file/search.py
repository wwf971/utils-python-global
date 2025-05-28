
import _utils_import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from collections import deque
else:
    deque = _utils_import.lazy_from_import("collections", "deque")

import _utils_file
def search_dir_path_with_dir_name(dir_path_base, dir_name_search, strict=True, recur=True, search_mode="bfs"):
    search_mode = search_mode.lower()
    if search_mode in ["bfs"]:
        return search_dir_path_with_dir_name_bfs(dir_path_base, dir_name_search, strict=strict, recur=True)
    elif search_mode in ["dfs"]:
        return search_dir_path_with_dir_name_dfs(dir_path_base, dir_name_search, strict=strict, recur=True)
    else:
        raise Exception


def search_dir_path_with_dir_name_dfs(dir_path_base, dir_name_search, strict=True, recur=True):
    for dir_name in _utils_file.list_all_dir_name(dir_path_base):
        if strict:
            if dir_name_search == dir_name.rstrip("/"):
                return dir_path_base + dir_name
        else:
            if dir_name_search.lower() in dir_name.rstrip("/").lower():
                return dir_path_base + dir_name
        
        result = search_dir_path_with_dir_name(
            dir_path_base=dir_path_base + dir_name,
            dir_name_search=dir_name_search,
            strict=strict,
            recur=recur
        )
        if result is not None:
            return result
        else:
            continue
    return None

def search_dir_path_with_dir_name_bfs(dir_path_base, dir_name_search, strict=True, recur=True):
    queue = deque([dir_path_base])

    while queue:
        current_dir = queue.popleft()

        for dir_name in _utils_file.list_all_dir_name(current_dir):
            subdir_path = current_dir + dir_name
            if strict:
                if dir_name_search == dir_name.rstrip("/"):
                    return subdir_path
            else:
                if dir_name_search.lower() in dir_name.rstrip("/").lower():
                    return subdir_path

            if recur:
                queue.append(subdir_path)

    return None