
import _thread # thread in python 2
def quit_function(fn_name):
    # print to stderr and flush immediately
    print('{0} took too long'.format(fn_name), file=sys.stderr)
    sys.stderr.flush() # flush stderr buffer
    _thread.interrupt_main() # raise a KeyboardInterrupt

def run_func_with_timeout(func, *args, timeout, backend="wrapt", **kwargs):
    backend = backend.lower()
    if backend in ["wrapt"]:
        return run_func_with_timeout_wrapt(func, *args, timeout, **kwargs)
    elif backend in ["thread"]:
        return run_func_with_timeout_thread(func, *args, timeout, **kwargs)
    elif backend in ["concurrent"]:
        # timeout: in seconds
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                # Wait for the result within the time limit
                result = future.result(timeout=timeout)
                is_timeout = False
            except concurrent.futures.TimeoutError:
                # Timeout occurred
                is_timeout = True
                result = None
        return is_timeout, result
    else:
        raise Exception

def run_func_with_timeout_wrapt(func, *args, timeout, **kwargs):
    # bug: cause error if some objects could not be properly serialized and deserialized by pickle
    # feature: effectively interrupt things like time.sleep(10) on Windows

    import wrapt_timeout_decorator # pip install wrapt_timeout_decorator
    # Wrap the function with a timeout using wrapt_timeout_decorator
    wrapped_func = wrapt_timeout_decorator.timeout(timeout)(func)
    try:
        # call the wrapped function with the given arguments
        result = wrapped_func(*args, **kwargs)
        return False, result
    except TimeoutError:
        # timeout occurred
        return True, None
    # except Exception: # exception from func
    #     return False, traceback.format_exc()

def run_func_with_timeout_thread(func, *args, timeout, **kwargs):
    import threading
    timer = threading.Timer(timeout, quit_function, args=[func.__name__])
    timer.start()
    try:
        result = func(*args, **kwargs)
        return result
    except Exception:
        print("timeout")
        return False, None
    finally:
        timer.cancel()

def run_func_with_timeout_multiple_trial(func, *args, timeout, trial_num, backend="auto", **kwargs):
    num = 0
    while num < trial_num:
        is_timeout, result = run_func_with_timeout(func, timeout, backend=backend, *args, **kwargs)
        if not is_timeout:
            return True, result
        num += 1
    return False, None