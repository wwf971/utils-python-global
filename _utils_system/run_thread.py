
import threading
def start_thread(func, *args, dependent=False, join=False, args_dict=None, **kwargs):
    """
    dependent=True   parent exit --> child exit
    dependent=False  parent exit --> child conitnue
        parent about to exit --> wait for all dependent=False child to exit --> parent really exit
    """
    if args_dict is not None:
        kwargs.update(args_dict)

    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.setDaemon(dependent) # the entire Python program exits when only dependent threads are left
    thread.start()
    if join:
        thread.join() # wait for child exit
    return thread
    # import _thread
    # try:
    #     _thread.start_new_thread(func, 
    #         args, # must be tuple. (xxx) is not a tuple. (xxx,) is a tuple.
    #     )
    # except:
    #     print ("Error: 无法启动线程")
