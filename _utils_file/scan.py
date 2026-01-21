
import os, re
from _utils_import import _utils_file

def list_all_file_name(dir_path):
    for f in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, f)):
            yield f

def list_all_file_path(dir_path, recur=False, _yield=True, exclude_dir_name=[]):
    if recur:
        if _yield:
            return list_all_file_path_in_tree(dir_path, order="depth_first", exclude_dir_name=exclude_dir_name)
        else:
            raise NotImplementedError
    if not dir_path.endswith("/") or dir_path.endswith("\\"):
        dir_path += "/"
    return [dir_path + file_name for file_name in list_all_file_name(dir_path)]

def list_all_file_name_and_path(dir_path, recur=False):
    if recur:
        # return list_all_file_path_in_tree(dir_path, order="depth_first")
        raise NotImplementedError
    if not dir_path.endswith("/") or dir_path.endswith("\\"):
        dir_path += "/"
    return [(file_name, dir_path + file_name) for file_name in list_all_file_name(dir_path)]

def list_all_file_name_with_name_pattern(dir_path, pattern: str, recur=False, _yield=True):
    if recur:
        raise NotImplementedError
    pattern_compiled = re.compile(pattern)
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)

    if _yield:
        for file_name in list_all_file_name(dir_path):
            if pattern_compiled.match(file_name) is not None:
                yield file_name
    else:
        file_name_list = []
        for file_name in list_all_file_name(dir_path):
            if pattern_compiled.match(file_name) is not None:
                file_name_list.append(file_name)
        return file_name_list
list_all_file_name_with_pattern = list_all_file_name_with_name_pattern

def list_all_file_path_with_name_pattern(dir_path, pattern: str, recur=False, _yield=True):
    if recur:
        raise NotImplementedError
    pattern_compiled = re.compile(pattern)
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)

    if _yield:
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is not None:
                yield file_name
    else:
        file_name_list = []
        for file_name in list_all_file_path(dir_path):
            if pattern_compiled.match(file_name) is not None:
                file_name_list.append(file_name)
        return file_name_list

from collections import deque
def list_all_file_path_in_tree(dir_path, order="depth_first", exclude_dir_name=[]):
    order = order.lower()
    if order in ["depth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.pop()
    elif order in ["breadth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.popleft()
    else:
        raise ValueError(order)

    dir_path = _utils_file.check_dir_exist(dir_path)
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    dir_path_list = deque([dir_path])

    while len(dir_path_list) > 0:
        dir_path_current = get_dir_path_next(dir_path_list)
        for file_name in _utils_file.list_all_file_name(dir_path_current):
            yield dir_path_current + file_name
        for dir_name in _utils_file.list_all_dir_name(dir_path_current):
            if dir_name.rstrip("/") in exclude_dir_name:
                continue
            dir_path_list.append(dir_path_current + dir_name)

def list_all_dir_name(dir_path, _yield=True):
    if _yield:
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                yield f + "/" 
    else:
        dir_name_list = [f + "/" for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        return dir_name_list

def list_all_dir_path(dir_path, _yield=True, recur=False):
    def _get_all_dirs(current_path):
        """helper function to recursively get all directory paths"""
        dirs = []
        try:
            for f in os.listdir(current_path):
                full_path = os.path.join(current_path, f)
                if os.path.isdir(full_path):
                    path_normed = _utils_file.dir_path_to_unix_style(full_path) + "/"
                    dirs.append(path_normed)
                    if recur:
                        dirs.extend(_get_all_dirs(full_path))
        except (PermissionError, OSError):
            # skip directories we can't access
            pass
        return dirs
    
    if _yield:
        def _yield_dirs(current_path):
            """Helper generator for yielding directory paths"""
            try:
                for f in os.listdir(current_path):
                    full_path = os.path.join(current_path, f)
                    if os.path.isdir(full_path):
                        path_normed = _utils_file.dir_path_to_unix_style(full_path) + "/"
                        yield path_normed
                        if recur:
                            yield from _yield_dirs(full_path)
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
        
        yield from _yield_dirs(dir_path)
    else:
        dir_path = _utils_file.dir_path_to_unix_style(dir_path)
        return _get_all_dirs(dir_path)

def list_all_dir_name_and_path(dir_path, _yield=True):
    if _yield:
        for f in os.listdir(dir_path):
            if os.path.isdir(os.path.join(dir_path, f)):
                yield (f + "/", dir_path + "/" + f + "/")
    else:  
        dir_path = _utils_file.dir_path_to_unix_style(dir_path)
        dir_path_list = [(f + "/", dir_path + "/" + f + "/") for f in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, f))]
        return dir_path_list

def list_all_file_path_and_dir_path(dir_path, _yield=True, recur=False):
    if recur:
        if _yield:
            return list_all_file_path_and_dir_path_in_tree(dir_path, order="depth_first")
        else:
            return list(list_all_file_path_and_dir_path_in_tree(dir_path, order="depth_first"))
    
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    if not dir_path.endswith("/"):
        dir_path += "/"
    
    if _yield:
        # Yield files first
        for file_name in list_all_file_name(dir_path):
            yield dir_path + file_name
        # Then yield directories
        for dir_name in list_all_dir_name(dir_path):
            yield dir_path + dir_name
    else:
        result = []
        # Add files first
        for file_name in list_all_file_name(dir_path):
            result.append(dir_path + file_name)
        # Then add directories
        for dir_name in list_all_dir_name(dir_path):
            result.append(dir_path + dir_name)
        return result

def list_all_file_path_and_dir_path_in_tree(dir_path, order="depth_first"):
    order = order.lower()
    if order in ["depth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.pop()
    elif order in ["breadth_first"]:
        get_dir_path_next = lambda dir_path_list: dir_path_list.popleft()
    else:
        raise ValueError(f"Invalid order: {order}")

    dir_path = _utils_file.check_dir_exist(dir_path)
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    dir_path_list = deque([dir_path])

    while len(dir_path_list) > 0:
        dir_path_current = get_dir_path_next(dir_path_list)
        
        # Yield all files in current directory
        for file_name in _utils_file.list_all_file_name(dir_path_current):
            yield dir_path_current + file_name
            
        # Yield all directories and add them to traversal queue
        for dir_name in _utils_file.list_all_dir_name(dir_path_current):
            dir_path_full = dir_path_current + dir_name
            yield dir_path_full
            dir_path_list.append(dir_path_full)

def list_all_file_name_with_suffix(dir_path: str, suffix: str):
    file_name_list = []
    suffix = suffix.lstrip(".")
    for file_name in list_all_file_name(dir_path):
        _, _suffix = _utils_file.get_file_name_and_suffix(file_name)
        if _suffix == suffix:
            file_name_list.append(file_name)
    return file_name_list

def list_all_file_path_with_suffix(dir_path: str, suffix: str):
    file_path_list = []
    suffix = suffix.lstrip(".")
    for file_name, file_path in list_all_file_name_and_path(dir_path):
        _, _suffix = _utils_file.get_file_name_and_suffix(file_name)
        if _suffix == suffix:
            file_path_list.append(file_path)
    return file_path_list

def visit_tree(dir_path_current, func=None, recur=True, verbose=False, dir_path_rel=None, func_dir=None, **kwargs):
    if dir_path_rel is None: # root
        dir_path_current = _utils_file.check_dir_exist(dir_path_current)
        dir_path_current = _utils_file.dir_path_to_unix_style(dir_path_current)
        dir_path_rel = ""
    if verbose:
        print(dir_path_current)
    if func: # func to address file
        for file_name in list_all_file_name(dir_path_current):
            func(
                dir_path_current=dir_path_current,
                file_name=file_name,
                dir_path_rel=dir_path_rel,
                **kwargs
            )
    if recur:
        for dir_name in list_all_dir_name(dir_path_current):
            visit_tree(
                dir_path_current=dir_path_current + dir_name, func=func,
                dir_path_rel=dir_path_rel + dir_name, # dir_name ends with "/"
                **kwargs
            )
            if func_dir:
                func_dir(
                    dir_path=dir_path_current + dir_name,
                    dir_path_rel=dir_path_rel + dir_name,
                    **kwargs
                )