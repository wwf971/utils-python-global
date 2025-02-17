from _utils_import import _utils, _utils_file, Dict, List
import _utils_train
import sys, os

def save_args(args: Dict, dir_path_instance=None):
    # store args in args.dir_path_instance
    if dir_path_instance is None:
        dir_path_instance = args.dir_path_instance

    _utils_file.obj_to_binary_file(args, dir_path_instance + 'config/args.dat')
    _utils_file.dict_to_json_file(args, dir_path_instance + 'config/args.jsonc')

    # # save as .json file
    # with open(json_file_path, 'w') as json_file:
    #     args_copy = dict(args)
    #     args_copy.pop("device")
    #     json.dump(args_copy, json_file, indent=4)

    # save cmd to save_dir_path
    with open(os.path.join(dir_path_instance, 'config/cmd.txt'), 'w') as f:
        f.write(' '.join(sys.argv))
        f.write('\n')
        f.write('pid: %s\n'%(str(os.getpid())))
        if args.hasattr('seed'):
            f.write('seed: %s\n'%(str(args.seed)))

class Config:
    def __init__(self):
        self.args = Dict()
        self.args_list = List()
        return
    def add_args(self, **kwargs):
        self.args_list.append(Dict(
            **kwargs
        ))
    def from_cmd_args(self, cmd_args: Dict):
        self.cmd_args = cmd_args
        import argparse
        if isinstance(cmd_args, argparse.Namespace):
            cmd_args = Dict(vars(cmd_args))
        self.add_args(
            type="cmd",
            content=cmd_args,
        )
        self.args = cmd_args
        return self
    def from_yaml_file(self, file_path_yaml):
        args_yaml = _utils.from_yaml_file(file_path_yaml)
        args_yaml = Dict(args_yaml)
        self.add_args(
            type="yaml",
            content=args_yaml,
            file_path=file_path_yaml
        )
        self.args.update(args_yaml)
        return self
    def set_dir_path_instance(self, dir_path_project):
        _utils_train.set_dir_path_instance(self.args, dir_path_project)
        return self
    def to_file(self, format=["binary", "yaml"]):
        if isinstance(format, str):
            format = [format]
        for _format in format:
            if _format in ["yaml"]:
                _utils.obj_to_yaml_file(self.args, self.args.dir_path_instance + 'config/args.yaml')
            elif _format in ["json", "jsonc"]:
                _utils_file.dict_to_json_file(self.args, self.args.dir_path_instance + 'config/args.jsonc')
            elif _format in ["binary"]:
                _utils_file.obj_to_binary_file(self.args, self.args.dir_path_instance + 'config/args.dat')
            else:
                raise ValueError
        return self
    def __getattr__(self, key):
        try:
            return self.args[key]
        except KeyError:
            raise AttributeError(f"'Dict' object has no attribute '{key}'")
    
    def get_device(self):
        if self.args.device is None or self.args.device in ["auto"]:
            device = _utils_train.get_device()
        else:
            device = self.args.device
        return device
    def init_tensorboard(self):
        log = _utils_train.init_tensorboard(self.args.dir_path_instance)
        return log