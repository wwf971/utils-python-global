

from __future__ import annotations


def run_episode(env, agent, turns = 3):
    total_scores = 0
    for j in range(turns):
        observation, info = env.reset()
        done = False
        while not done:
            # take deterministic actions at test time
            action, logprob_a = agent.select_action(observation, deterministic=True)
            observation_next, reward, dw, tr, info = env.step(action)
            done = (dw or tr)

            total_scores += reward
            observation = observation_next
    return int(total_scores/turns)