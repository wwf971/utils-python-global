if __name__=="__main__":
    import sys, os, pathlib
    DirPathCurrent = os.path.dirname(os.path.realpath(__file__)) + "/"
    DirPathParent = pathlib.Path(DirPathCurrent).parent.absolute().__str__() + "/"
    DirPathGrandParent = pathlib.Path(DirPathParent).parent.absolute().__str__() + "/"
    DirPathGreatGrandParent = pathlib.Path(DirPathGrandParent).parent.absolute().__str__() + "/"
    sys.path += [
        DirPathCurrent, DirPathParent, DirPathGrandParent, DirPathGreatGrandParent
    ]

    from _utils_file import (
        get_dir_path_of_file_path,
        get_file_path_without_suffix,
    )
    from _utils_torch.utils import print_torch_module
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
    dir_path_current = get_dir_path_of_file_path(__file__)
    save_file_path = get_file_path_without_suffix(__file__) + "-model.dat"
    model_2 = model.to_file(save_file_path).from_file(save_file_path)
    print(model_2)
    # mlp.register_parameter(
    #     "a.b", torch.nn.Parameter(torch.Tensor((10, 10)))
    # ) # => KeyError: 'parameter name can\'t contain "."'
    #     # use this rule to exclude parameters
    print_torch_module(model_2)