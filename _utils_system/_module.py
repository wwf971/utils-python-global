
def load_module_from_file(file_path_script):
    # load a .py script file as module
    import importlib.util
    _utils_file.check_file_exist(file_path_script)

    # get the module name by stripping the directory and file extension
    module_name = os.path.splitext(os.path.basename(file_path_script))[0]

    # load the module spec
    spec = importlib.util.spec_from_file_location(module_name, file_path_script)
        # module_name can be any string
    module_loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module_loaded)
    return module_loaded

def import_class_from_file(file_path_script, class_name):
    module_loaded = load_module_from_file(file_path_script)

    # retrieve the class from the loaded module
    if hasattr(module_loaded, class_name):
        return getattr(module_loaded, class_name)
    else:
        raise AttributeError(f"Class {class_name} not found in {file_path_script}")