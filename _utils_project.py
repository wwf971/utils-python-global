from _utils_import import _utils_io, _utils_file

def CleanEmptySubDir(dir_path, pipe_out=None):
    if not _utils_file.file_exist(dir_path):
        return
    """
    """

    if pipe_out is None:
        pipe_out = _utils_io.PipeOut()
    for subdir_path in _utils_file.list_all_dir_path(dir_path):

        _utils_file.remove_dir_if_is_empty(subdir_path)
        pipe_out.print("remove_dir")
        with pipe_out.increased_indent():
            pipe_out.print("DIR_PATH: %s"%subdir_path)

    for DirName in DirNameList:
        DirPath = BaseDirPath + DirName
        if DLUtils.file.IsEmptyDir(DirPath):
            DLUtils.file.RemoveDir(DirPath)
            assert not DLUtils.file.ExistsDir(DirPath)
            if pipe_out is not None:
                pipe_out.print("Removed empty dir.")
                with pipe_out.IncreasedIndent():
                    pipe_out.print("DirPath: %s"%DirPath)
    return

from DLUtils.file import (
    GetDirPathWithSameDirNameAsFile,
    GetFilePathWithoutSuffix,
    DeleteFileIfExists
)

def GetProjectDirPath(FilePath):
    """
    
    """
    FilePathNoSuffix, Suffix = DLUtils.file.SeparateFileNameSuffix(FilePath)
    BaseDirPath = FilePathNoSuffix + "/"
    BaseDirPath = DLUtils.EnsureDir(BaseDirPath)
    return BaseDirPath

