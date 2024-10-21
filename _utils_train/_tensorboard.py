from __future__ import annotations
import _utils_file

from tensorboard.backend.event_processing import event_accumulator
class TensorboardWrapper():
    def __init__(self, dir_path):
        self.dir_path_tensorboard = dir_path
        dir_path = _utils_file.dir_path_to_unix_style(dir_path)
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(log_dir=dir_path)
        self.file_path_tensorboard = _utils_file.get_file_latest_create(dir_path)
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
    def load(self, file_path_tensorboard):
        # Path to your TensorBoard log file
        # file_path: like 'events.out.tfevents.1716735260'
            # 1716735260 is unix time stamp, which is number of seconds passed since 1970/01/01 00:00
        _utils_file.check_file_exist(file_path_tensorboard)
        self.file_path_tensorboard = file_path_tensorboard
        self.load_ea()
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

def init_tensorboard(dir_path) -> TensorboardWrapper:
    # build SummaryWriter to record train curves
    import shutil
    _utils_file.remove_file_if_exist
    log = TensorboardWrapper(dir_path)
    # name of log file is automatically generated. could not be modified.
        # 2024-09-06 17:05:36.515603: I tensorflow/core/util/port.cc:110] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
        # 2024-09-06 17:05:36.576936: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
        # To enable the following instructions: AVX2 AVX512F AVX512_VNNI FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
        # DEBUG:tensorflow:Falling back to TensorFlow client; we recommended you install the Cloud TPU client directly with pip install cloud-tpu-client.
        # 2024-09-06 17:05:38.596909: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
    # writer.add_scalar('test', 1.0, global_step=0) # test
    return log
