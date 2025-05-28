import multiprocessing
from _utils_import import _utils_file, _utils_io, _utils_system, Dict
import sys, os, time
def run(
    func, config,
    args=(), kwargs={}
):
    with _utils_io.StdOutAndStdErrToFile(
        file_path_stdout=config.file_path_stdout,
        file_path_stderr=config.file_path_stderr,
        file_mode="ab",
    ):
        with open(config.file_path_info, "w", encoding="utf-8") as f:
            print(f"child pid={_utils_system.get_current_process_pid()}", file=f)
        func(*args, **kwargs)

def run_repeat(
    func, args=(), kwargs={},
    config: Dict=None
):
    if not config.hasattr("parent"): config.parent = Dict()
    config.parent.setdefault("file_path_stdout", _utils_file.get_file_path_current_no_suffix(__file__) + "~stdout.txt")
    config.parent.setdefault("file_path_stderr", _utils_file.get_file_path_current_no_suffix(__file__) + "~stderr.txt")
    config.parent.setdefault("file_path_info",   _utils_file.get_file_path_current_no_suffix(__file__) + "~info.txt")

    dir_path_current = os.path.dirname(os.path.realpath(__file__)) + "/"
    if not config.hasattr("child"): config.child = Dict()
    config.child.setdefault("file_path_stdout", dir_path_current + "log.txt",)
    config.child.setdefault("file_path_stderr", dir_path_current + "log-err.txt",)
    config.child.setdefault("file_path_info",   dir_path_current + "log-info.txt")

    if not config.hasattr("run"): config.run = Dict()
    config.run.setdefault("num", 100)
    config.run.setdefault("interval", 5)
    config.run.setdefault("interval_inc", None)
    config.run.setdefault("interval_max", None)

    trial_index = 0

    with open(config.parent.file_path_info, "a", encoding="utf-8") as f:
        print(f"pid={_utils_system.get_current_process_pid()}", file=f)

    with _utils_io.StdOutAndStdErrToFile(
        file_path_stdout=config.parent.file_path_stdout,
        file_path_stderr=config.parent.file_path_stderr,
        file_mode="ab",
    ):
        interval_current = config.run.interval
        while trial_index < config.run.num:
            print(f"TRIAL={trial_index}")

            # run as independent process
            process = multiprocessing.Process(target=run, kwargs=Dict(
                func = func, args=args, kwargs=kwargs,
                config=config.child,
            ))

            process.start()
            process.join()
            
            if process.exitcode == 0:
                print("SUCCESS. process exits with 0")
                break
            
            trial_index += 1
            time.sleep(interval_current)
            if config.run.interval_inc:
                interval_current += config.run.interval_inc
                if interval_current > config.run.interval_max:
                    interval_current = config.run.interval_max

        if trial_index >= config.run.num:
            with open(config.parent.file_path_stderr, "a", encoding="utf-8") as e:
                print(f"ERROR: still fail after {trial_index} trial.", file=sys.stderr)