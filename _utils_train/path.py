from _utils_import import _utils_file

import re
def get_model_file_path_by_epoch(dir_path_instance, epoch, pattern = r"model-epoch(.*)\.dat"):    
    file_name_list = []
    for file_name in _utils_file.list_all_file_name(dir_path_instance + "model/"):
        result = re.match(file_name, pattern)
        if result is None:
            continue
        else:
            if isinstance(epoch, str):
                if result.group(1) == epoch:
                    file_name_list.append(file_name)
            elif isinstance(epoch, int):
                if int(result.group(1)) == epoch:
                    file_name_list.append(file_name)

    if len(file_name_list) == 0:
        return None
    elif len(file_name_list) == 1:
        return _utils_file.dir_path_to_unix_style(dir_path_instance) + file_name_list[0]
    else:
        raise Exception
    
def set_dir_path_instance(args, dir_path_base):
    # dir_path_instance: directory path to store current experiment data)
    if not args.hasattr("dir_path_instance"):
        import _utils_time
        time_str = _utils_time.get_current_time_str_ymd8_hms8()
        dir_path_instance = dir_path_base + "experiment/" + time_str + "/"
    _utils_file.create_dir_if_not_exist(dir_path_instance)
    args.setattr(dir_path_instance=dir_path_instance)
