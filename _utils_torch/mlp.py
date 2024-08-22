from _utils_import import torch, nn, F
import _utils_torch
from .wrapper import TorchModuleWrapper, ModuleList

def get_torch_nonlinear_func(nonlinear_func_str: str):
    nonlinear_func_str = nonlinear_func_str.lower()
    if nonlinear_func_str in ["relu"]:
        return nn.ReLU
    elif nonlinear_func_str in ["tanh"]:
        return nn.Tanh
    elif nonlinear_func_str in ["sigmoid"]:
        return nn.Sigmoid
    else:
        raise ValueError

class NonLinearLayer(TorchModuleWrapper):
    def init(self, input_size, output_size, nonlinear_func="relu"):
        config = self.config
        config.nonlinear_func = nonlinear_func
        config.input_size = input_size
        config.output_size = output_size
        
        self.add_torch_module("nonlinear_func", get_torch_nonlinear_func(config.nonlinear_func))
        
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
    def init(self, *layer_unit_num, nonlinear_func="relu"):
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
    
def build_mlp(layer_shape, hidden_activation, output_activation):
    layers = []
    for j in range(len(layer_shape)-1):
        act = hidden_activation if j < len(layer_shape)-2 else output_activation
        layers += [nn.Linear(layer_shape[j], layer_shape[j+1]), act()]
    return nn.Sequential(*layers)

class ParallelMLPLayer(TorchModuleWrapper):
    def init(self, **kwargs):
        super().init(**kwargs)
        config = self.config
        linear_layer_list = [
            nn.Linear(in_features=config.input_size, out_features=config.output_size) for _ in range(config.mlp_num)
        ]
        weight = torch.stack([linear_layer.weight for linear_layer in linear_layer_list], axis=0).permute(0, 2, 1)
            # (mlp_num, input_size, output_size)
        bias = torch.stack([linear_layer.bias for linear_layer in linear_layer_list])
            # (mlp_num, output_size)
        _utils_torch.check_tensor_shape(weight, config.mlp_num, config.input_size, config.output_size)
        _utils_torch.check_tensor_shape(bias, config.mlp_num, config.output_size)
        self.add_param(weight=weight, bias=bias)
        self.add_torch_module("nonlinear_func", get_torch_nonlinear_func(config.nonlinear_func))
        
    def forward(self, x): # x: (batch_size, mlp_num, input_dim)
        # x_unsqueeze = x.unsqueeze(1) # (batch_size, mlp_num, input_dim)
        # y = torch.bmm(x_unsqueeze, self.weight)
        y = torch.einsum('bmi,mio->bmo', x, self.weight) # (batch_size, mlp_num, output_dim)
        z = self.nonlinear_func(y).squeeze(1) + self.bias
        return z

class ParallelMLP(ModuleList):
    def init(self, *layer_unit_num, mlp_num, nonlinear_func):
        assert len(layer_unit_num) >= 2
        config = self.config
        config.layer_unit_num = layer_unit_num
        config.layer_num = len(layer_unit_num) - 1
        config.input_size = layer_unit_num[0]
        config.hidden_size = layer_unit_num[1:-1]
        config.output_size = layer_unit_num[-1] # size of last layer
        config.mlp_num = mlp_num
    
        self.act = nonlinear_func
        for layer_index in range(len(layer_unit_num)-1):
            input_size = layer_unit_num[layer_index]
            output_size = layer_unit_num[layer_index + 1]
            self.add_submodule(
                "layer-%d"%layer_index, ParallelMLPLayer(
                    input_size=input_size, output_size=output_size,
                    mlp_num=mlp_num, nonlinear_func=nonlinear_func
                )
            )
    def build(self):
        config = self.config
        self.mlp_num = config.mlp_num
        return super().build()
    def forward(self, x): # (batch_size, input_size)
        y = x.unsqueeze(1).repeat(1, self.mlp_num, 1) # (batch_size, mlp_num, input_size)
        for submodule in self.module_list:
            z = submodule(y)
            y = z
        return z

class Multi_Q_Critic(TorchModuleWrapper):
    def init(self, q_num, hidden_size, input_dim, output_dim):
        super().init(
            q_num=q_num, hidden_size=hidden_size, input_dim=input_dim, output_dim=output_dim
        )
        self.add_module(
            mlp = ParallelMLP(*[input_dim, *hidden_size, output_dim], mlp_num=q_num)
        )
    def forward(self, x): # (batch_size, mlp_num, 1)
        y = self.mlp(x)
        z = y.squeeze(2)
        return z

