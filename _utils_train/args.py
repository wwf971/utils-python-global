from _utils_import import _utils, _utils_file, Dict
import sys, os

def save_args(args: Dict, dir_path_instance=None):
    # save args to save_dir_path
    import json
    import pickle
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