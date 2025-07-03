from stable_baselines3 import PPO
from stable_baselines3.common.envs import DummyVecEnv
from gym import Env
import numpy as np
import pandas as pd
from drl.database_loader import load_training_data

class TradingEnv(Env):
    def __init__(self, df):
        super(TradingEnv, self).__init__()
        self.df = df
        self.action_space = gym.spaces.Discrete(3)  # 0: HOLD, 1: BUY, 2: SELL
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(3,), dtype=np.float32)
        self.current_step = 0

    def reset(self):
        self.current_step = 0
        return self._get_obs()

    def _get_obs(self):
        row = self.df.iloc[self.current_step]
        return np.array([row["price"], row["sentiment_score"], row["price_change_pct"]], dtype=np.float32)

    def step(self, action):
        reward = 0
        done = self.current_step >= len(self.df) - 1
        info = {}

        # Simple reward scheme: simulate returns
        if action == 1:  # BUY
            reward = self.df.iloc[self.current_step]["price_change_pct"]
        elif action == 2:  # SELL
            reward = -self.df.iloc[self.current_step]["price_change_pct"]

        self.current_step += 1
        return self._get_obs(), reward, done, info

def train():
    df = load_training_data()
    env = DummyVecEnv([lambda: TradingEnv(df)])
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=5000)
    model.save("drl_trading_model")

if __name__ == "__main__":
    import gym
    train()
