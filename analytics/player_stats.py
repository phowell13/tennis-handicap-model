import pandas as pd
from pathlib import Path

DATA_PATH = Path("data") / "2026-wta-season.csv"

def load_raw() -> pd.DataFrame:
    # Auto-detect delimiter (comma, tab, semicolon, etc.)
    return pd.read_csv(DATA_PATH, sep=None, engine="python")

def build_player_surface_stats(df: pd.DataFrame) -> pd.DataFrame:
    # HOME rows
    home = df.rename(columns={
        "home_name": "player",
        "home_service_points_won_perc": "srv_pts_won",
        "home_return_points_won_perc": "ret_pts_won",
        "home_break_points_won_perc": "bp_won",
        "home_break_points_saved_perc": "bp_saved",
    })[
        ["player", "surface", "season_year",
         "srv_pts_won", "ret_pts_won", "bp_won", "bp_saved"]
    ]

    # AWAY rows
    away = df.rename(columns={
        "away_name": "player",
        "away_service_points_won_perc": "srv_pts_won",
        "away_return_points_won_perc": "ret_pts_won",
        "away_break_points_won_perc": "bp_won",
        "away_break_points_saved_perc": "bp_saved",
    })[
        ["player", "surface", "season_year",
         "srv_pts_won", "ret_pts_won", "bp_won", "bp_saved"]
    ]

    # Combine
    long = pd.concat([home, away], ignore_index=True)

    # Aggregate per player/surface/season
    agg = (
        long
        .dropna(subset=["srv_pts_won", "ret_pts_won"])
        .groupby(["player", "surface", "season_year"])
        .agg(
            matches=("srv_pts_won", "count"),
            srv_pts_won=("srv_pts_won", "mean"),
            ret_pts_won=("ret_pts_won", "mean"),
            bp_won=("bp_won", "mean"),
            bp_saved=("bp_saved", "mean"),
        )
        .reset_index()
    )

    return agg

def get_player_profile(agg: pd.DataFrame, player: str,
                       surface: str = "clay", season: int = 2026) -> dict:

    subset = agg[
        (agg["player"] == player) &
        (agg["surface"].str.lower() == surface.lower()) &
        (agg["season_year"] == season)
    ]

    if subset.empty:
        raise ValueError(f"No stats for {player} on {surface} in {season}")

    row = subset.sort_values("matches", ascending=False).iloc[0]

    return {
        "name": row["player"],
        "surface": row["surface"],
        "season": int(row["season_year"]),
        "matches": int(row["matches"]),
        "srv_pts_won": row["srv_pts_won"] / 100.0,
        "ret_pts_won": row["ret_pts_won"] / 100.0,
        "bp_won": row["bp_won"] / 100.0,
        "bp_saved": row["bp_saved"] / 100.0,
    }
