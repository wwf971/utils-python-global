from _utils_import import _utils, _utils_file, Dict, List
import sys, os

def save_args(args: Dict, dir_path_instance=None):
    # save args to save_dir_path
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
    def from_cmd_args(self, args):
        self.args = args
        import argparse
        if isinstance(args, argparse.Namespace):
            args = Dict(vars(args))
        self.add_args(args, "cmd")
        self.args_cmd = args
    def from_yaml_file(self, file_path_yaml):
        args_yaml = _utils.from_yaml_file(file_path_yaml)
        args_yaml = Dict(args_yaml)
        self.add_args(args_yaml, "yaml")
        self.args.update(args_yaml)