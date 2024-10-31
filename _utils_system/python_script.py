import _utils_system
import _utils_file
import sys, subprocess

def run_python_script_method(file_path_script, func_name, *args, **kwargs):
    _utils_file.check_file_exist(file_path_script)
    # load the module spec
    module = _utils_system.import_module_from_file(file_path_script)
    # get the method from the module
    func = getattr(module, func_name)
    # run the method with any provided arguments
    return func(*args, **kwargs)

def run_python_script(
    file_path_script,
    backend:str="subprocess",
    join=False,
    dependent=True, # if dependent, parent exit --> child exit.
    cmd_args=None,
    file_path_python=None,
    pass_parent_pid=False,
    **kwargs
):
    _utils_file.check_file_exist(file_path_script)
    backend = backend.lower()

    if cmd_args is None: 
        # cnd_args=[] in func param is dangerous.
        # same [] object might be used in different thread
        cmd_args = []

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
        if join: # dependent=True, join=True
            print("run_python_script_subprocess")
            run_python_script_thread(
                file_path_script=file_path_script,
                cmd_args=cmd_args,
                on_output=on_output,
                file_path_python=file_path_python,
                args_dict={
                    "join": True,
                    "depedent": True # --> start_process
                },
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
                args_dict={
                    "join": False,
                    "depedent": True # --> start_process
                },
                dependent=True, # --> start_thread
                join=False,
                **kwargs
            )
    else:
        raise NotImplementedError

def run_python_script_thread(file_path_script, cmd_args=[], file_path_python=None, on_output=None, return_output=False, join=True, dependent=True, **kwargs):    
    if file_path_python is None:
        file_path_python = sys.executable # python executable running this line

    cmd_line = [
        "%s"%file_path_python,
        "-u", # -u: do not buffer stdout/stderr
        "%s"%file_path_script,
    ]
    for arg in cmd_args:
        cmd_line.append(arg)
    
    cmd_line_str = " ".join(cmd_line)
    if on_output:
        on_output("cmd_line: %s"%cmd_line_str)
    print("cmd_line: %s"%cmd_line_str)
    
    if return_output:
        exit_code, stdout_bytes, stderr_bytes = _utils_system.start_process(
            cmd_line, on_output=on_output, return_output=return_output,
            join=join, dependent=dependent,
            backend="subprocess"
        )
        return exit_code, stdout_bytes, stderr_bytes
    else:
        exit_code = _utils_system.start_process(
            cmd_line, on_output=on_output, return_output=return_output,
            join=join, dependent=dependent,
            backend="subprocess"
        )
        return exit_code

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