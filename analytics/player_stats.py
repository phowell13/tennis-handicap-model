# analytics/player_stats.py
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data") / "2026-wta-season.csv"

def load_stats():
    return pd.read_csv(DATA_PATH)

def get_player_surface_row(df, player_name: str, surface: str = "clay"):
    df_p = df[df["player"] == player_name]
    if "surface" in df.columns:
        df_p = df_p[df_p["surface"] == surface]
    # last row / latest date / best aggregation – we can refine once I see columns
    return df_p.sort_values("date").iloc[-1]

