import _utils_system
import os, subprocess
from _utils_import import Dict

def start_process(
    cmd_line, dir_path_console=None,
    on_output=None,
    print_output=False,
    return_output=False,
    dependent=False,
    join=False,
    backend="subprocess",
    **kwargs
):
    backend = backend.lower()
    if backend == "subprocess":
        if join:
            return run_cmd_line_subprocess(
                cmd_line=cmd_line, dir_path_console=dir_path_console,
                on_output=on_output, print_output=print_output, return_output=return_output,
                dependent=dependent,
                **kwargs
            )
        else:
            return _utils_system.start_thread(
                run_cmd_line_subprocess,
                cmd_line=cmd_line, on_output=on_output, print_output=print_output, return_output=return_output,
                dependent=dependent, # --> start_thread
                args_dict={"dependent": dependent} # --> start_process
            )
        return
    else:
        raise Exception
run_cmd_line = start_process

def run_cmd_line_subprocess(
    cmd_line, dir_path_console=None,
    on_output=None, print_output=True, return_output=False,
    dependent=True, verbose=True
):
    if isinstance(cmd_line, list):
        pass
    elif isinstance(cmd_line, str):
        pass # shell must be True in subprocess.Popen
    else:
        raise TypeError

    if return_output:
        stdout_bytes = []
        stderr_bytes = []

    if on_output is not None:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                if return_output:
                    if stream_name == "STDOUT": stdout_bytes.append(line_bytes)
                    else: stderr_bytes.append(line_bytes)
                on_output(line_str)
            stream.close()
    else:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                if print_output:
                    print(f"{stream_name}: {line_str}")
                if return_output:
                    if stream_name == "STDOUT": stdout_bytes.append(line_bytes)
                    else: stderr_bytes.append(line_bytes)
            stream.close()

    if on_output:
        on_output("cmd_line: %s"%cmd_line)
    if verbose:
        print("cmd_line: %s"%cmd_line)

    if dependent and _utils_system.is_win():
        if _utils_system.is_win():
            try: # use windows job to further ensure child process is dependent
                import win32api # https://stackoverflow.com/questions/23434842
                import win32con
                import win32job
                hJob = win32job.CreateJobObject(None, "")
                extended_info = win32job.QueryInformationJobObject(hJob, win32job.JobObjectExtendedLimitInformation)
                extended_info['BasicLimitInformation']['LimitFlags'] = win32job.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                win32job.SetInformationJobObject(hJob, win32job.JobObjectExtendedLimitInformation, extended_info)
            except Exception:
                pass
    
    if dir_path_console is None:
        dir_path_console = os.getcwd()

    # create the subprocess
    if dependent:
        process = subprocess.Popen(
            cmd_line,
            cwd=dir_path_console,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # text=True, # set to True to get str instead of bytes
            bufsize=1,  # line-buffered output
            shell=True  # set to True if you're using shell commands
        )
    else: # independent process
        process = subprocess.Popen(
            cmd_line,
            cwd=dir_path_console,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # text=True, # set to True to get str instead of bytes
            bufsize=1,  # line-buffered output
            shell=True,  # set to True if you're using shell commands
            creationflags=subprocess.DETACHED_PROCESS, # | subprocess.CREATE_NEW_PROCESS_GROUP,
                # creationflags=0x00000008, # DETACHED_PROCESS
        )

    if dependent and _utils_system.is_win():
        try:
            # Convert process id to process handle:
            perms = win32con.PROCESS_TERMINATE | win32con.PROCESS_SET_QUOTA
            hProcess = win32api.OpenProcess(perms, False, process.pid)
            win32job.AssignProcessToJobObject(hJob, hProcess)
        except Exception:
            pass

    # create threads for stdout and stderr
    thread_stdout = _utils_system.start_thread(read_output, process.stdout, stream_name="STDOUT", dependent=True, join=False)
    thread_stderr = _utils_system.start_thread(read_output, process.stderr, stream_name="STDERR", dependent=True, join=False)

    # wait for the process to finish
    process.wait()

    # wait for the threads to finish
    thread_stdout.join(0.2)
    thread_stderr.join(0.2)

    # if on_output:
    #     on_output("run_cmd_line_subprocess: exit")
    # print("run_cmd_line_subprocess: exit")
    exit_code = process.returncode

    if return_output:
        return Dict(exit_code=exit_code, stdout=stdout_bytes, stderr=stderr_bytes)
    else:
        return Dict(exit_code=exit_code)