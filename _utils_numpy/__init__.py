from _utils_import import np, pd

def np_array_to_text_file(np_array, file_path_save, **Dict):
    dim_num = len(np_array.shape)
    if dim_num == 2:
        np_array_2d_to_text_file(np_array, file_path_save=file_path_save, **Dict)
    else:
        raise NotImplementedError

def np_array_to_str(Data, **Dict):
    DimNum = len(Data.shape)    
    if DimNum == 2:
        DataStr = np_array_2d_to_str(Data, **Dict)
        Name = Dict.setdefault("Name", "NpArray")
        Shape = str(Data.shape)
        Info = "{0}. Shape: {1}".format(Name, list(Shape))
        Dim = "Dim 0 / Dim 1"
        return "\n".join([Name, Shape, Dim, DataStr])
    else:
        raise Exception()

def np_array_2d_to_str(np_array, col_name_list=None, row_name=None):
    assert len(np_array.shape) == 2
    dict_pd= {}
    if col_name_list is None:
        col_name_list = ["Col %d"%ColIndex for ColIndex in range(np_array.shape[1])]
    
    for col_index, col_name in enumerate(col_name_list):
        dict_pd[col_name] = np_array[:, col_index]
    
    if row_name is not None:
        raise NotImplementedError
    
    return pd.DataFrame(dict_pd).to_string()

def np_array_2d_to_text_file(Data, ColName=None, RowName=None, SavePath=None):
    assert SavePath is not None
    str_list = []
    str_shape = "shape: %s\n"%(str(Data.shape))
    str_list.append(str_shape)
    if len(Data.shape) == 1:
        Data = Data[:, np.newaxis]
    np_array_str = np_array_2d_to_str(Data, ColName=ColName, RowName=RowName, SavePath=SavePath)
    str_list.append(np_array_str)
    # if WriteStat:
    #     StrStat = DLUtils.math.NpArrayStatisticsStr(Data, verbose=False)
    #     StrList.append(StrStat)
    import _utils_file
    _utils_file.str_to_text_file("".join(np_array_str), FilePath=SavePath)