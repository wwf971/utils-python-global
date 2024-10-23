import _utils_system
import subprocess

def start_process(cmd_line, on_output, print_output=False, return_output=False, daemon=False, join=False, backend="subprocess", **kwargs):
    backend = backend.lower()
    if backend == "subprocess":
        return
    else:
        raise Exception
    return

def run_cmd_line(cmd_line, on_output=None, print_output=True, return_output=False):
    if isinstance(cmd_line, list):
        pass
    elif isinstance(cmd_line, str):
        pass
    else:
        raise TypeError
    
    if return_output:
        stdout_line = []
        stderr_line = []

    if on_output is not None:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                if return_output:
                    if stream_name == "STDOUT": stdout_line.append(line_str)
                    else: stderr_line.append(line_str)
                on_output(line_str)
            stream.close()
    else:
        def read_output(stream, stream_name):
            for line_bytes in iter(stream.readline, b''):
                line_str = line_bytes.decode('utf-8', errors='replace').rstrip('\r\n').rstrip('\n')
                if print_output:
                    print(f"{stream_name}: {line_str}")
                if return_output:
                    if stream_name == "STDOUT": stdout_line.append(line_str)
                    else: stderr_line.append(line_str)
            stream.close()

    if on_output:
        on_output("cmd_line: %s"%cmd_line)
    print("cmd_line: %s"%cmd_line)

    # create the subprocess
    process = subprocess.Popen(
        cmd_line,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # text=True, # set to True to get str instead of bytes
        bufsize=1,  # line-buffered output
        shell=True  # set to True if you're using shell commands
    )

    # create threads for stdout and stderr
    thread_stdout = _utils_system.start_thread(read_output, process.stdout, stream_name="STDOUT", daemon=True, join=False)
    thread_stderr = _utils_system.start_thread(read_output, process.stderr, stream_name="STDERR", daemon=True, join=False)

    # wait for the process to finish
    process.wait()

    # wait for the threads to finish
    thread_stdout.join(0.2)
    thread_stderr.join(0.2)

    if on_output:
        on_output("run_python_script: exit")
    print("run_python_script: exit")
    exit_code = process.returncode

    if return_output:
        return exit_code, stdout_line, stderr_line
    else:
        return exit_code