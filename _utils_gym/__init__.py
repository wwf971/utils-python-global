

def create_env(env_name, Seed=None, RenderMode="rgb_array"):
    """
    RenderMode: 决定了env.render()的返回值.
        "rgb_array": 返回值
    """
    import gym
    env = gym.make(env_name, render_mode=RenderMode)
    
    if Seed is not None:
        set_seed_for_env(env, Seed)
    return env

def create_vec_env(EnvName, Num: int, Seed, ):
    """
    parallel env.
    """
    assert len(Seed) == Num
    return env

def set_seed_for_env(Env, Seed):
    return

def get_act_dim(env):
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.shape[0]

def get_state_dim(env):
    """
    observation is a flattened 1-d vector.
    """

    return


from _utils_mujoco import SetMujocoRenderBackend
from .video import VideoRecorder
