import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_parent = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_grand_parent = pathlib.Path(dir_path_parent).parent.absolute().__str__() + "/"
dir_path_great_grand_parent = pathlib.Path(dir_path_grand_parent).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_parent, dir_path_grand_parent, dir_path_great_grand_parent
]

from _utils_import import _utils_file

from _utils_torch.utils import print_torch_module
def unit_test_mlp():
    import sys, os, pathlib
    DirPathCurrent = os.path.dirname(os.path.realpath(__file__)) + "/"
    DirPathParent = pathlib.Path(DirPathCurrent).parent.absolute().__str__() + "/"
    DirPathGrandParent = pathlib.Path(DirPathParent).parent.absolute().__str__() + "/"
    DirPathGreatGrandParent = pathlib.Path(DirPathGrandParent).parent.absolute().__str__() + "/"
    sys.path += [
        DirPathCurrent, DirPathParent, DirPathGrandParent, DirPathGreatGrandParent
    ]

    from _utils_torch.mlp import MLP
    # example usage:
    model = MLP().init(10, 20, 30, 40).build()
    print(model)
    base_dir_path = _utils_file.get_dir_path_of_file_path(__file__)
    save_file_path = base_dir_path + "mlp.dat"
    model_2 = model.to_file(save_file_path).from_file(save_file_path)
    print(model_2)
    # mlp.register_parameter(
    #     "a.b", torch.nn.Parameter(torch.Tensor((10, 10)))
    # ) # => KeyError: 'parameter name can\'t contain "."'
    #     # use this rule to exclude parameters
    print_torch_module(model_2)
    return

def unit_test_parallel_mlp():
    from _utils_torch.mlp import MLPParallel, torch
    model = MLPParallel(10, 20, 30, mlp_num=10, nonlinear_func="relu").build()
    import _utils_math
    input_example = torch.from_numpy(_utils_math.sample_from_gaussian_01((64, 10))).float() # (batch_size, input_size)
    output_example = model(input_example) # (batch_size, mlp_num, output_size)
    print_torch_module(model)
    base_dir_path = get_dir_path_of_file_path(__file__)
    save_file_path = base_dir_path + "mlp.dat"
    model_2 = model.to_file(save_file_path).from_file(save_file_path)
    print_torch_module(model_2)
    return

if __name__=="__main__":
    unit_test_parallel_mlp()
    pass