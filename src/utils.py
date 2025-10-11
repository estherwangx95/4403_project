# src/utils.py
import pandas as pd
import matplotlib.pyplot as plt

def collect_data(model):
    df = pd.DataFrame({
        "time": range(len(model.sales)),
        "sales": model.sales
    })
    return df

def visualize(df):
    plt.plot(df["time"], df["sales"])
    plt.xlabel("Time Step")
    plt.ylabel("Sales Volume")
    plt.title("Community Group Buying Dynamics")
    plt.show()