import sys, os, time
from _utils_import import psutil
import _utils_system
def process_exist(pid):
    if _utils_system.is_win():
        # return psutil.pid_exists(pid) # if the process exited recently, a pid may still exist for the handle
        try: # https://stackoverflow.com/questions/568271
            process = psutil.Process(pid)
        except psutil.Error as error:  # includes NoSuchProcess error
            return False
        if psutil.pid_exists(pid) and process.status() not in (psutil.STATUS_DEAD, psutil.STATUS_ZOMBIE):
            return True
        return False
    else:
        try:
            os.kill(pid, 0) # sending signal 0 will terminate an existing process
        except OSError: # if OSError is raised, the process does not exist
            return False
        else:
            return True # if no exception is raised, the process exists

def _exit_if_another_process_exit(pid):
    while True:
        time.sleep(1.0)
        if not _utils_system.process_exist(pid):
            # sys.exit(0) # only exit this thread
            os._exit(-1)

def exit_if_another_process_exit(pid):
    _utils_system.start_thread(
        _exit_if_another_process_exit,
        pid=pid,
        join=False,
        dependent=True
    )

def exit_if_parent_process_exit(parent_pid=None):
    if parent_pid is None: # get parent_pid from cmd_args
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--parent_pid', type=int, default=-1, help='parent process id')
        # args = parser.parse_args()
        args = parser.parse_known_args()[0]
        parent_pid = args.parent_pid
        if args.parent_pid < 0:
            print("cannot parse parent_pid from cmd_args")
            return
    exit_if_another_process_exit(parent_pid)

def get_current_process_pid():
    return os.getpid()