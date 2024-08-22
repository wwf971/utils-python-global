import torch.nn as nn
from .wrapper import TorchModuleWrapper, ModuleList

class NonLinearLayer(TorchModuleWrapper):
    def init(self, input_size, output_size, nonlinear_func="ReLU"):
        config = self.config
        config.nonlinear_func = nonlinear_func
        config.input_size = input_size
        config.output_size = output_size
        if nonlinear_func in ["ReLU", "relu"]:
            self.add_submodule("nonlinear_func", nn.ReLU())
        else:
            raise ValueError

        self.add_torch_module(
            "linear_map",
            nn.Linear,
            in_features=config.input_size,
            out_features=config.output_size,
            bias=True
        )
        return self
    def forward(self, x):
        return self.nonlinear_func(self.linear_map(x))

class MLP(ModuleList):
    def init(self, *layer_unit_num, nonlinear_func="ReLU"):
        assert len(layer_unit_num) >= 2
        config = self.config
        config.layer_unit_num = layer_unit_num
        config.layer_num = len(layer_unit_num) - 1
        config.input_size = layer_unit_num[0]
        config.hidden_size = layer_unit_num[1:-1]
        config.output_size = layer_unit_num[-1] # size of last layer
        
        input_size = config.input_size
        layer_index = 0
        for layer_index in range(config.layer_num):
            input_size  = config.layer_unit_num[layer_index]
            output_size = config.layer_unit_num[layer_index + 1]
            layer = NonLinearLayer().init(input_size, output_size, nonlinear_func)
            self.add_submodule("layer-%d"%layer_index, layer)
        return self