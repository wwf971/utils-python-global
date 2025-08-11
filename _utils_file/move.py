from _utils_import import _utils_file
from _utils_import import shutil
import re
from pathlib import Path

def move_file(file_path_source, file_path_target, overwrite=False):
    assert _utils_file.file_exist(file_path_source)
    if not overwrite:
        assert not _utils_file.file_exist(file_path_target)
    _utils_file.create_dir_for_file_path(file_path_target)
    shutil.move(file_path_source, file_path_target)
    # Path(file_path_source).rename(file_path_target)
        # [WinError 17] 系统无法将文件移到不同的磁盘驱动器。
    assert not _utils_file.file_exist(file_path_source)
    assert _utils_file.file_exist(file_path_target)

def move_file_verbose(file_path_source, file_path_target, overwrite=False, pipe_out=None):
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    pipe_out.print("FILE_MOVE")
    _utils_file.create_dir_for_file_path(file_path_target)
    move_file(file_path_source, file_path_target, overwrite=overwrite)
    with pipe_out.increased_indent():
        pipe_out.print(f"FROM: {file_path_source}")
        pipe_out.print(f"TO  : {file_path_target}")
    return

def copy_file_verbose(file_path_source, file_path_target, pipe_out=None):
    copy_file(file_path_source, file_path_target)
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    pipe_out.print("FILE_COPY")
    with pipe_out.increased_indent():
        pipe_out.print(f"FROM: {file_path_source}")
        pipe_out.print(f"TO  : {file_path_target}")
    return

def copy_file(file_path_source, file_path_target):
    assert _utils_file.file_exist(file_path_source)
    _utils_file.create_dir_for_file_path(file_path_target)
    shutil.copy2(file_path_source, file_path_target) # copy2() preseves timestamp. copy() does not.
    assert _utils_file.file_exist(file_path_target)
    return

def rename_file_verbose(dir_path, file_name, file_name_new, pipe_out=None):
    result = rename_file(dir_path, file_name, file_name_new)
    if pipe_out is None:
        import _utils_io
        pipe_out = _utils_io.PipeOut()
    pipe_out.print("FILE_RENAME")
    with pipe_out.increased_indent():
        pipe_out.print(f"FROM: {dir_path + file_name}")
        pipe_out.print(f"TO  : {dir_path + file_name_new}")
    return result

def rename_file(dir_path, file_name, file_name_new):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    file_path = dir_path + file_name
    file_path_new = dir_path + file_name_new
    move_file(file_path, file_path_new)

def rename_dir(dir_path, dir_name_new):
    dir_path = _utils_file.dir_path_to_unix_style(dir_path)
    dir_path_parent = _utils_file.get_dir_path_of_dir_path(dir_path)
    dir_path_new = dir_path_parent + dir_name_new
    assert _utils_file.dir_exist(dir_path)
    assert not _utils_file.dir_exist(dir_path_new)
    Path(dir_path).rename(dir_path_new)
    assert not _utils_file.dir_exist(dir_path)
    assert _utils_file.dir_exist(dir_path_new)

def move_file_overwrite(file_path_source, file_path_target):
    assert _utils_file.file_exist(file_path_source)
    Path(file_path_source).rename(file_path_target)
    assert not _utils_file.file_exist(file_path_source)
    assert _utils_file.file_exist(file_path_target)

def move_if_file_name_match_pattern(
    dir_path,
    dir_path_target,
    pattern=None,
):
    pattern_compiled = re.compile(pattern)
    dir_path_target = _utils_file.dir_path_to_unix_style(dir_path)
    for file_name in _utils_file.list_all_file_name(dir_path):
        if pattern_compiled.match(file_name) is not None:
            _utils_file.move_file(dir_path + file_name, dir_path_target + file_name)

def copy_file_by_time_modify(file_path_source, file_path_target, verbose=True):
    from .content import (
        files_have_same_content,
        get_file_size,
    )
    from _utils_file import (
        get_file_modify_unix_stamp,
        file_exist,
        file_path_to_unix_style,
    )

    # Normalize paths
    file_path_source = file_path_to_unix_style(file_path_source)
    file_path_target = file_path_to_unix_style(file_path_target)

    # Ensure source exists
    if not file_exist(file_path_source):
        raise FileNotFoundError(f"Source file does not exist: {file_path_source}")

    should_copy = False
    if not file_exist(file_path_target):
        should_copy = True
    else:
        source_time = get_file_modify_unix_stamp(file_path_source)
        target_time = get_file_modify_unix_stamp(file_path_target)
        if source_time > target_time:
            should_copy = True
        elif source_time == target_time and not files_have_same_content(file_path_source, file_path_target):
            should_copy = True

    if should_copy:
        if verbose:
            copy_file_verbose(file_path_source, file_path_target)
        else:
            copy_file(file_path_source, file_path_target)

    return

def copy_dir_by_time_modify(
    dir_path_source, dir_path_target,
    incremental=True,
    incremental_exclude_dir_name=[],
    verbose=True, pipe_out=None,
    exclude_dir_name=[],
    exclude_file_name=[],
):
    from .content import (
        files_have_same_content,
        get_file_size,
    )
    from _utils_file import (
        get_file_modify_unix_stamp,
        file_exist,
        dir_exist,
        list_all_file_name,
        list_all_dir_name,
        dir_path_to_unix_style,
    )
    from collections import deque
    import os

    # Normalize paths
    dir_path_source = dir_path_to_unix_style(dir_path_source)
    dir_path_target = dir_path_to_unix_style(dir_path_target)

    # Ensure source exists
    if not dir_exist(dir_path_source):
        raise FileNotFoundError(f"Source directory does not exist: {dir_path_source}")

    # Create target if it doesn't exist
    if not dir_exist(dir_path_target):
        os.makedirs(dir_path_target, exist_ok=True)

    # Initialize queue with root directory
    queue = deque([(dir_path_source, dir_path_target)])

    while queue:
        current_source, current_target = queue.popleft()

        # Process all files in current directory
        for file_name in list_all_file_name(current_source):
            # Skip files that are in the exclude list
            if file_name in exclude_file_name:
                if verbose and pipe_out:
                    pipe_out.print(f"Skipping excluded file: {file_name}")
                continue

            source_file = current_source + file_name
            target_file = current_target + file_name

            should_copy = False
            if not file_exist(target_file):
                should_copy = True
            else:
                source_time = get_file_modify_unix_stamp(source_file)
                target_time = get_file_modify_unix_stamp(target_file)
                if source_time > target_time:
                    should_copy = True
                elif source_time == target_time and not files_have_same_content(source_file, target_file):
                    should_copy = True

            if should_copy:
                if verbose:
                    copy_file_verbose(source_file, target_file)
                else:
                    copy_file(source_file, target_file)

        # Add subdirectories to queue
        for dir_name in list_all_dir_name(current_source):
            # Skip directories that are in the exclude list
            if dir_name.rstrip("/") in exclude_dir_name:
                if verbose and pipe_out:
                    pipe_out.print(f"Skipping excluded directory: {dir_name}")
                continue
                
            next_source = current_source + dir_name + "/"
            next_target = current_target + dir_name + "/"
            
            if not dir_exist(next_target):
                os.makedirs(next_target, exist_ok=True)
            
            queue.append((next_source, next_target))

        # If not incremental, remove files and directories in target that don't exist in source
        if not incremental:
            # Remove files that don't exist in source
            for file_name in list_all_file_name(current_target):
                source_file = current_source + file_name
                target_file = current_target + file_name
                if not file_exist(source_file):
                    message = f"FILE_DELETE. file not in source: {target_file}"
                    if verbose and pipe_out:
                        pipe_out.print(message)
                    elif verbose:
                        print(message)
                    os.remove(target_file)
            
            # Remove directories that don't exist in source
            for dir_name in list_all_dir_name(current_target):
                # Skip excluded directories
                if dir_name.rstrip("/") in exclude_dir_name:
                    continue
                
                # Skip directories in incremental_exclude_dir_name when not in incremental mode
                if dir_name.rstrip("/") in incremental_exclude_dir_name:
                    if verbose and pipe_out:
                        pipe_out.print(f"Skipping incremental-excluded directory from deletion: {dir_name}")
                    continue
                    
                source_dir = current_source + dir_name + "/"
                target_dir = current_target + dir_name + "/"
                if not dir_exist(source_dir):
                    message = f"DIR_DELETE. dir not in source: {target_dir}"
                    if verbose and pipe_out:
                        pipe_out.print(message)
                    elif verbose:
                        print(message)
                    import shutil
                    shutil.rmtree(target_dir)

    return

def move_dir(dir_path_source, dir_path_target, overwrite=False, recur=True, verbose=True):
    from .content import (
        get_file_size,
        files_have_same_content
    )
    from _utils_file import (
        file_exist,
        dir_exist,
        list_all_file_name,
        list_all_dir_name,
        dir_path_to_unix_style,
    )
    from collections import deque
    import os
    import shutil

    # Normalize paths
    dir_path_source = dir_path_to_unix_style(dir_path_source)
    dir_path_target = dir_path_to_unix_style(dir_path_target)

    # Ensure source exists
    if not dir_exist(dir_path_source):
        raise FileNotFoundError(f"Source directory does not exist: {dir_path_source}")

    # Create target if it doesn't exist
    if not dir_exist(dir_path_target):
        os.makedirs(dir_path_target, exist_ok=True)

    # Process all files in current directory
    for file_name in list_all_file_name(dir_path_source):
        source_file = dir_path_source + file_name
        target_file = dir_path_target + file_name

        if file_exist(target_file):
            # Check if files are identical
            if files_have_same_content(source_file, target_file):
                if verbose:
                    print(f"FILE_REMOVE: {source_file}")
                os.remove(source_file)
            else:
                if verbose:
                    print(f"FILE_SKIP (different content exists): {source_file}")
        else:
            # Move the file
            if verbose:
                print(f"FILE_MOVE:")
                print(f"    file_path_1: {source_file}")
                print(f"    file_path_2: {target_file}")
            shutil.move(source_file, target_file)
            # check if file is moved
            assert not _utils_file.file_exist(source_file)
            assert _utils_file.file_exist(target_file)

    # Handle subdirectories if recursive
    if recur:
        for dir_name in list_all_dir_name(dir_path_source):
            source_subdir = dir_path_source + dir_name + "/"
            target_subdir = dir_path_target + dir_name + "/"

            # Create target subdirectory if it doesn't exist
            if not dir_exist(target_subdir):
                os.makedirs(target_subdir, exist_ok=True)

            # Recursively move subdirectory contents
            move_dir(source_subdir, target_subdir, overwrite, recur, verbose)

        # Remove empty source directories after moving their contents
        for dir_name in list_all_dir_name(dir_path_source):
            source_subdir = dir_path_source + dir_name + "/"
            try:
                os.rmdir(source_subdir)  # Will only remove if directory is empty
                if verbose:
                    print(f"Removed empty directory: {source_subdir}")
            except OSError:
                if verbose:
                    print(f"Could not remove directory (not empty): {source_subdir}")

    return