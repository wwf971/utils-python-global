from __future__ import annotations
import sys

class StdOutAndErrToFileAndTerminal:
    def __init__(self, print_file_path):
        self.print_file_path = print_file_path
    def __enter__(self):
        import _utils_file
        _utils_file.create_dir_for_file_path(self.print_file_path)
        f = open(self.print_file_path, "w")
        self.pipe = MultiPipe(f, sys.__stdout__)
        self.f = f
        self.stdout_prev = sys.stdout
        self.stderr_prev = sys.stderr
        sys.stdout = self.pipe
        sys.stderr = self.pipe
    def __exit__(self, type, value, trace):
        sys.stdout = self.stdout_prev
        sys.stderr = self.stderr_prev
        self.f.close()

class StdOutToFileAndTerminal:
    def __init__(self, file_path):
        self.print_file_path = file_path
    def __enter__(self):
        import _utils_file
        _utils_file.create_dir_for_file_path(self.print_file_path)
        f = open(self.print_file_path, "w")
        self.pipe = MultiPipe(f, sys.__stdout__)
        self.stdout_prev = sys.stdout
        sys.stdout = self.pipe
        self.f = f
    def __exit__(self, type, value, trace):
        sys.stdout = self.stdout_prev
        self.f.close()

class StdErrToFileAndTerminal:
    def __init__(self, file_path):
        self.file_path = file_path
    def __enter__(self):
        f = open(self.file_path, "w")
        self.pipe = MultiPipe(f, sys.__stderr__)
        self.stderr_prev = sys.stderr
        sys.stderr = self.pipe
        self.f = f
    def __exit__(self, type, value, trace):
        sys.stderr = self.stderr_prev
        self.f.close()

class MultiPipe:
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()  # flush the output to ensure it's written

    def flush(self):
        for f in self.files:
            f.flush()
    
if __name__ == "__main__":
    import sys, os, pathlib
    DirPathCurrent = os.path.dirname(os.path.realpath(__file__)) + "/"
    DirPathParent = pathlib.Path(DirPathCurrent).parent.absolute().__str__() + "/"
    DirPathGrandParent = pathlib.Path(DirPathParent).parent.absolute().__str__() + "/"
    DirPathGreatGrandParent = pathlib.Path(DirPathGrandParent).parent.absolute().__str__() + "/"
    sys.path += [
        DirPathCurrent, DirPathParent, DirPathGrandParent, DirPathGreatGrandParent
    ]
    import _utils_file
    with StdOutToFileAndTerminal(_utils_file.get_file_path_without_suffix(__file__) + "/stdout.txt"):
        with StdErrToFileAndTerminal(_utils_file.get_file_path_without_suffix(__file__) + "/stderr.txt"):
            print("output to stdout", file=sys.stdout)
            print("output to stderr", file=sys.stderr)
    
    with StdOutAndErrToFileAndTerminal(_utils_file.get_file_path_without_suffix(__file__) + "/stdout_stderr.txt"):
        print("output to stdout and stderr")