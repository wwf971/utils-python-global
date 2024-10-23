from __future__ import annotations
import _utils_file
import _utils_train

from tensorboard.backend.event_processing import event_accumulator
class TensorboardWrapper():
    def __init__(self, dir_path=None):
        if dir_path is not None:
            self.init(dir_path)

        from collections import defaultdict
        self._cache_float = defaultdict(lambda:_utils_train.FloatLog())
        self._cache_int   = defaultdict(lambda:_utils_train.IntLog())

    def init(self, dir_path):
        self.dir_path_tensorboard = dir_path
        dir_path = _utils_file.dir_path_to_unix_style(dir_path)
        _utils_file.create_dir_if_not_exist(dir_path)
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(log_dir=dir_path)
        self.file_path_tensorboard = self.get_file_path_tensorboard_from_dir_path(dir_path)
        print("file_path_tensorboard: %s"%self.file_path_tensorboard)
        if self.file_path_tensorboard is None:
            raise Exception
    def cache_float(self, global_step=None, batch_size=None, **kwargs):
        for key, value in kwargs.items():
            self._cache_float[key].append(value, batch_size)
            return
    def cache_int(self, global_step=None, batch_size=None, **kwargs):
        for key, value in kwargs.items():
            self._cache_float[key].append(value, batch_size)
            return
    def cache_flush(self, global_step):
        for key, value in dict(self._cache_float).items():
            self.add_float(
                key, value.report_avg(),
                global_step=global_step
            )
            value.clear()
        for key, value in dict(self._cache_int).items():
            self.add_int(
                key, value.report_avg(),
                global_step=global_step
            )
            value.clear()
        return
    def get_file_path_tensorboard_from_dir_path(self, dir_path):
        file_path_list = []
        for file_name, file_path in _utils_file.list_all_file_name_and_path(dir_path):
            if "tfevents" in file_name:
                file_path_list.append(file_path)
        if len(file_path_list) > 1:
            print("multiple tensorboard file detected.")
            file_path = _utils_file.get_file_latest_create_from_file_list(file_path_list)
        elif len(file_path_list) == 1:
            file_path = file_path_list[0]
        else:
            None
        return file_path
    def log_epoch_begin(self, epoch_index, global_step):
        self.add_int(epoch_begin=epoch_index, global_step=global_step)
    def get_epoch_begin_step_list(self):
        if hasattr(self, "epoch_begin_step_list"):
            return self.epoch_begin_step_list
        epoch_begin_events = self.get_event_int("epoch_begin")
        self.epoch_begin_step_list = [event.step for event in epoch_begin_events]
        self.epoch_begin_step_list.sort()
        return self.epoch_begin_step_list
    def get_epoch_and_batch_index(self, global_step):
        epoch_begin_step_list = self.get_epoch_begin_step_list()
        import _utils_math
        epoch_begin_step, epoch_index = _utils_math.find_max_element_less_than(global_step, epoch_begin_step_list)
        if epoch_begin_step is None:
            return None, None
        else:
            batch_index = global_step - epoch_begin_step
            return epoch_index, batch_index
    def load_from_instance_dir(self, dir_path_instance):
        dir_path_instance = _utils_file.dir_path_to_unix_style(dir_path_instance)
        dir_path = dir_path_instance + "log/"
        _utils_file.check_dir_exist(dir_path)
        self.file_path_tensorboard = self.get_file_path_tensorboard_from_dir_path(dir_path)
        print("file_path_tensorboard: %s"%self.file_path_tensorboard)
        if self.file_path_tensorboard is None:
            raise Exception
        self.load_ea()
        return self
    def load_from_file(self, file_path_tensorboard):
        # Path to your TensorBoard log file
        # file_path: like 'events.out.tfevents.1716735260'
            # 1716735260 is unix time stamp, which is number of seconds passed since 1970/01/01 00:00
        _utils_file.check_file_exist(file_path_tensorboard)
        self.file_path_tensorboard = file_path_tensorboard
        self.load_ea()
    def get_file_path_tensorboard(self):
        return self.file_path_tensorboard
    def add_int(self, global_step=None, **kwargs):
        for key, value in kwargs.items():
            self.writer.add_scalar(
                key, value, global_step=global_step 
            )

    def add_float(self, global_step=None, **kwargs):
        for key, value in kwargs.items():
            self.writer.add_scalar(
                key, value, global_step=global_step 
            )
    def flush(self):
        # make sure that data is saved to disk
        self.writer.flush()
    def list_all_float(self):
        return self.ea.Tags().get('scalars', [])
    def get_event_float(self, name):
        return self.ea.Scalars(name)
    def get_event_int(self, name):
        return self.ea.Scalars(name)
    def reload(self):
        self.load_ea()
    def load_ea(self):
        # initialize the EventAccumulator
        self.ea = event_accumulator.EventAccumulator(self.file_path_tensorboard,
            size_guidance={
                event_accumulator.COMPRESSED_HISTOGRAMS: 500,
                event_accumulator.IMAGES: 4,
                event_accumulator.AUDIO: 4,
                event_accumulator.SCALARS: 0,
                event_accumulator.HISTOGRAMS: 1,
            })
        # load the events from the file
        self.ea.Reload()
    def print_tags(self):
        # print the available tags (variables) in the log file
        tags = self.ea.Tags()
        print("Available tags:")
        for tag_type in tags:
            print(f"{tag_type}: {tags[tag_type]}")

def init_tensorboard(dir_path_instance) -> TensorboardWrapper:
    # build SummaryWriter to record train curves
    import shutil
    dir_path_instance = _utils_file.dir_path_to_unix_style(dir_path_instance)
    dir_path_tensorboard = dir_path_instance + "log/"
    log = TensorboardWrapper(dir_path_tensorboard)
    # name of log file is automatically generated. could not be modified.
        # 2024-09-06 17:05:36.515603: I tensorflow/core/util/port.cc:110] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
        # 2024-09-06 17:05:36.576936: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
        # To enable the following instructions: AVX2 AVX512F AVX512_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
        # DEBUG:tensorflow:Falling back to TensorFlow client; we recommended you install the Cloud TPU client directly with pip install cloud-tpu-client.
        # 2024-09-06 17:05:38.596909: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
    # writer.add_scalar('test', 1.0, global_step=0) # test
    return log
