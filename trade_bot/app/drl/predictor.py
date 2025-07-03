from stable_baselines3 import PPO
import numpy as np
import os

MODEL_PATH = "drl/drl_trading_model.zip"

# Load trained model
model = PPO.load(MODEL_PATH)

def prepare_observation(price: float, sentiment_score: float, price_change_pct: float):
    """
    Formats the observation into the format expected by the DRL model.
    """
    return np.array([[price, sentiment_score, price_change_pct]], dtype=np.float32)

def predict_action(price: float, sentiment_score: float, price_change_pct: float):
    """
    Returns DRL model's action: 0=HOLD, 1=BUY, 2=SELL
    """
    obs = prepare_observation(price, sentiment_score, price_change_pct)
    action, _ = model.predict(obs)
    return int(action)
