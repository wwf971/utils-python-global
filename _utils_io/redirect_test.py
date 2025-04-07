import sys, os, pathlib
dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path_1 = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
dir_path_2 = pathlib.Path(dir_path_1).parent.absolute().__str__() + "/"
dir_path_3 = pathlib.Path(dir_path_2).parent.absolute().__str__() + "/"
dir_path_4 = pathlib.Path(dir_path_3).parent.absolute().__str__() + "/"
dir_path_5 = pathlib.Path(dir_path_4).parent.absolute().__str__() + "/"
sys.path += [
    dir_path_current, dir_path_1, dir_path_2 , dir_path_3, dir_path_4, dir_path_5
]

import time
from redirect import (
    RedirectStdOutAndStdErrToFile,
    RedirectStdOutAndStdErrToBytesIO
)

if __name__ == "__main__":
    import sys, os, pathlib
    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    dir_path_1 = pathlib.Path(dir_path_current).parent.absolute().__str__() + "/"
    dir_path_2 = pathlib.Path(dir_path_1).parent.absolute().__str__() + "/"
    dir_path_3 = pathlib.Path(dir_path_2).parent.absolute().__str__() + "/"
    dir_path_4 = pathlib.Path(dir_path_3).parent.absolute().__str__() + "/"
    dir_path_5 = pathlib.Path(dir_path_4).parent.absolute().__str__() + "/"
    sys.path += [
        dir_path_current, dir_path_1, dir_path_2 , dir_path_3, dir_path_4, dir_path_5
    ]
    from _utils_import import _utils_file
    print("std.out+std.err-->bytes_io begin")
    with RedirectStdOutAndStdErrToBytesIO() as f:
        # print("print to stdout and stderr")
        # print("std.out+std.err-->bytes_io begin")
        print("print to stdout", file=sys.stdout)
        print("print to stderr", file=sys.stderr)
        print("print to sys.__stdout__", file=sys.__stdout__)
        print("print to sys.__stderr__", file=sys.__stderr__)
        # print("std.out+std.err-->bytes_io end")
        print("") # add one empty line
        # time.sleep(1.0)
    print("std.out+std.err-->bytes_io end")
    
    # 打印f.buffer中的内容
    # data = _utils_io.read_from_string_io(f.buffer, clear_buf=False)
    # print(data.decode("utf-8"))

    file_path = _utils_file.get_file_path_no_suffix(__file__) + "-std.out+std.err.txt"
    print("std.out+std.err-->file begin")
    print("file_path: %s"%(file_path))
    with RedirectStdOutAndStdErrToFile(
        file_path=file_path,
        pipe_prev=f # print content in this pipe.
    ):
        # print("std.out+std.err-->file begin")
        print("print to stdout and stderr")
        print("print to stdout", file=sys.stdout)
        print("print to stderr", file=sys.stderr)
        print("print to sys.__stdout__", file=sys.__stdout__)
        print("print to sys.__stderr__", file=sys.__stderr__)
        # time.sleep(1.0)
        # print("std.out+std.err-->file end")
    print("std.out+std.err-->file end")
    time.sleep(1.0)

# expected content in shell:
    # std.out+std.err-->bytes_io begin
    # std.out+std.err-->bytes_io end
    # std.out+std.err-->file begin
    # file_path: redirect_test-std.out+std.err.txt
    # print to stdout
    # print to stderr
    # print to sys.__stdout__
    # print to sys.__stderr__

    # print to stdout and stderr
    # print to stdout
    # print to stderr
    # print to sys.__stdout__
    # print to sys.__stderr__
    # std.out+std.err-->file end

# expected content in file:
    # std.out+std.err-->bytes_io begin
    # print to stdout
    # print to stderr
    # print to sys.__stdout__
    # print to sys.__stderr__
    # std.out+std.err-->bytes_io end

    # std.out+std.err-->file begin
    # print to stdout and stderr
    # print to stdout
    # print to stderr
    # print to sys.__stdout__
    # print to sys.__stderr__
    # std.out+std.err-->file end