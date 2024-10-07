



import _utils_torch

from _utils_torch import TorchModuleWrapper, MLPParallel

class Multi_Q_Critic(TorchModuleWrapper):
    def init(self, q_num, hidden_size, input_dim, output_dim):
        super().init(
            q_num=q_num, hidden_size=hidden_size, input_dim=input_dim, output_dim=output_dim
        )
        self.add_module(
            mlp = MLPParallel(*[input_dim, *hidden_size, output_dim], mlp_num=q_num)
        )
    def forward(self, x): # (batch_size, mlp_num, 1)
        y = self.mlp(x)
        z = y.squeeze(2)
        return z