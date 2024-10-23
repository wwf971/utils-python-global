import _utils_system
import _utils_file
import sys, subprocess

def run_python_script_method(file_path_script, func_name, *args, **kwargs):
    _utils_file.check_file_exist(file_path_script)
    # load the module spec
    module = _utils_system.load_module_from_file(file_path_script)
    # get the method from the module
    func = getattr(module, func_name)
    # run the method with any provided arguments
    return func(*args, **kwargs)

def run_python_script(
    file_path_script,
    backend:str="subprocess",
    join=False,
    dependent=True, # if dependent, parent exit --> child exit.
    cmd_args=[],
    file_path_python=None,
    pass_parent_pid=False,
    **kwargs
):
    _utils_file.check_file_exist(file_path_script)
    backend = backend.lower()

    if pass_parent_pid:
        import _utils_system
        parent_pid = _utils_system.get_current_process_pid()
        cmd_args += ["--parent_pid", "%d"%parent_pid]

    if backend in ["subprocess"]:
        run_python_script_subprocess(
            file_path_script,
            file_path_python=file_path_python,
            cmd_args=cmd_args,
            join=join,
            dependent=dependent,
            **kwargs
        )
    else:
        raise NotImplementedError
    return

def run_python_script_subprocess(
    file_path_script, cmd_args=[], file_path_python=None, on_output=None,
    dependent=True, join=True, **kwargs
):
    if dependent: # parent exit --> child exit
        if join: # dependent=True, join=False
            run_python_script_thread(
                file_path_script=file_path_script,
                cmd_args=cmd_args,
                on_output=on_output,
                file_path_python=file_path_python,
                **kwargs
            )
            # elif method == 'select':
            #     run_python_script_select(
            #         file_path_script=file_path_script,
            #         cmd_args=cmd_args,
            #     )
        else: # dependent=True, join=False
            _utils_system.start_thread(
                run_python_script_thread,
                file_path_script=file_path_script,
                cmd_args=cmd_args,
                on_output=on_output,
                file_path_python=file_path_python,
                dependent=True,
                join=False,
                **kwargs
            )
    else:
        raise NotImplementedError

def run_python_script_thread(file_path_script, cmd_args=[], file_path_python=None, on_output=None):
    if on_output is not None:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                on_output(line_str)
            stream.close()
    else:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                print(f"{stream_name}: {line_str}")
            stream.close()
    
    if file_path_python is None:
        file_path_python = sys.executable # python executable running this line

    cmd_line = "\"%s\" -u \"%s\""%(file_path_python, file_path_script)
        # -u: do not buffer stdout/stderr
    for arg in cmd_args:
        cmd_line += " %s"%arg

    if on_output:
        on_output("cmd_line: %s"%cmd_line)
    print("cmd_line: %s"%cmd_line)

    # create the subprocess
    process = subprocess.Popen(
        cmd_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # text=True,  # set to True to get str instead of bytes
        bufsize=1,  # line-buffered output
        shell=True,  # set to True if you're using shell commands
    )

    # create threads for stdout and stderr
    thread_stdout = _utils_system.start_thread(read_output, process.stdout, stream_name="STDOUT", dependent=True, join=False)
    thread_stderr = _utils_system.start_thread(read_output, process.stderr, stream_name="STDERR", dependent=True, join=False)

    # wait for the process to finish
    process.wait()

    # wait for the threads to finish
    thread_stdout.join(0.2)
    thread_stderr.join(0.2)

    if on_output:
        on_output("run_python_script: exit")
    print("run_python_script: exit")

def run_python_script_select(file_path_script, cmd_args=[], file_path_python=None):
    import select
    if file_path_python is None:
        file_path_python = sys.executable # python executable running this line

    cmd_line = "\"%s\" -u \"%s\""%(file_path_python, file_path_script)
        # -u: do not buffer stdout/stderr
    for arg in cmd_args:
        cmd_line += " %s"%arg

    print(cmd_line)

    process = subprocess.Popen(
        cmd_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # text=True,  # set to True to get str instead of bytes
        bufsize=1,  # line-buffered output
        shell=True  # set to True if you're using shell commands
    )

    # continuously read stdout and stderr
    try:
        # 基于select. cross-platform不如基于thread
        ready_to_read, _, _ = select.select(
            [process.stdout, process.stderr], [], []
        )
        while True:
            for stream in ready_to_read:
                if stream == process.stdout:
                    stdout_line = stream.readline()
                    if stdout_line:
                        print(f"STDOUT: {stdout_line.strip()}")
                elif stream == process.stderr:
                    stderr_line = stream.readline()
                    if stderr_line:
                        print(f"STDERR: {stderr_line.strip()}")

            # Break the loop if the process has finished
            if process.poll() is not None:
                break

    except KeyboardInterrupt:
        # If you want to terminate the process on KeyboardInterrupt
        print("Terminating the process...")
        process.terminate()
        return

    # wait for the process to finish
    process.stdout.close()
    process.stderr.close()
    process.wait()
    print("process_exit.")
    return

def run_python_script_test():
    run_python_script(r"S:\Project-Code\python-script\1-file\file-event-watch.py")
    return