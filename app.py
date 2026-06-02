"""
Streamlit app for a WTA tennis handicap model.

Put this file at the ROOT of your GitHub repo, next to README.md and requirements.txt.
Run locally with:

    streamlit run app.py

The app lets you upload a WTA match CSV, select two players, choose a surface,
and produce fair odds for game handicaps from -4.5 to +4.5.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# Make imports work whether your modules are at repo root or inside /analytics.
# Recommended repo layout:
#   app.py
#   analytics/player_stats.py
#   analytics/serve_return_model.py
#   analytics/simulator.py
# -----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
ANALYTICS_DIR = ROOT / "analytics"
if ANALYTICS_DIR.exists():
    sys.path.insert(0, str(ANALYTICS_DIR))

try:
    from player_stats import build_player_surface_stats
    from serve_return_model import build_hold_return_profile
    from simulator import MatchConfig, handicap_cover_prob_mc
except ImportError as exc:
    st.error(
        "Could not import model files. Make sure app.py is in the repo root and "
        "player_stats.py, serve_return_model.py, and simulator.py are either in "
        "the root or in an analytics/ folder."
    )
    st.exception(exc)
    st.stop()


REQUIRED_COLUMNS = {
    "season_year",
    "surface",
    "home_name",
    "away_name",
    "home_service_points_won_perc",
    "away_service_points_won_perc",
    "home_return_points_won_perc",
    "away_return_points_won_perc",
    "home_break_points_won_perc",
    "away_break_points_won_perc",
    "home_break_points_saved_perc",
    "away_break_points_saved_perc",
}


st.set_page_config(
    page_title="WTA Handicap Fair Value Model",
    page_icon="🎾",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def read_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """Read uploaded CSV and normalise obvious formatting issues."""
    df = pd.read_csv(uploaded_file, sep=None, engine="python")
    df.columns = [str(c).strip() for c in df.columns]

    # Keep only finished, real matches if those columns exist.
    if "status" in df.columns:
        df = df[df["status"].astype(str).str.upper().eq("FINISHED")]
    if "status_extra" in df.columns:
        df = df[df["status_extra"].astype(str).str.upper().eq("FINISHED")]

    # Convert numeric columns used by the model.
    numeric_cols = [
        "season_year",
        "home_service_points_won_perc",
        "away_service_points_won_perc",
        "home_return_points_won_perc",
        "away_return_points_won_perc",
        "home_break_points_won_perc",
        "away_break_points_won_perc",
        "home_break_points_saved_perc",
        "away_break_points_saved_perc",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "surface" in df.columns:
        df["surface"] = df["surface"].astype(str).str.strip().str.lower()

    return df


@st.cache_data(show_spinner=False)
def build_stats(df: pd.DataFrame) -> pd.DataFrame:
    return build_player_surface_stats(df)


def validate_columns(df: pd.DataFrame) -> list[str]:
    missing = sorted(REQUIRED_COLUMNS.difference(df.columns))
    return missing


def available_players(df: pd.DataFrame) -> list[str]:
    players = pd.concat([df["home_name"], df["away_name"]], ignore_index=True)
    return sorted(players.dropna().astype(str).unique())


def available_surfaces(df: pd.DataFrame) -> list[str]:
    surfaces = sorted(df["surface"].dropna().astype(str).str.lower().unique())
    return ["all"] + surfaces


def get_profile(agg: pd.DataFrame, player: str, surface: str, season: int) -> Dict:
    """
    Similar to player_stats.get_player_profile(), but supports surface='all'.
    It returns weighted season-level averages for the selected player.
    """
    subset = agg[(agg["player"] == player) & (agg["season_year"] == season)].copy()

    if surface != "all":
        subset = subset[subset["surface"].astype(str).str.lower() == surface.lower()]

    if subset.empty:
        raise ValueError(f"No usable stats for {player} on {surface} in {season}.")

    total_matches = float(subset["matches"].sum())
    weights = subset["matches"] / total_matches

    return {
        "name": player,
        "surface": surface,
        "season": int(season),
        "matches": int(total_matches),
        "srv_pts_won": float((subset["srv_pts_won"] * weights).sum() / 100.0),
        "ret_pts_won": float((subset["ret_pts_won"] * weights).sum() / 100.0),
        "bp_won": float((subset["bp_won"] * weights).sum() / 100.0),
        "bp_saved": float((subset["bp_saved"] * weights).sum() / 100.0),
    }


def fair_odds(probability: float) -> float | None:
    if probability <= 0:
        return None
    return 1.0 / probability


def format_decimal_odds(x: float | None) -> str:
    if x is None or not np.isfinite(x):
        return "—"
    return f"{x:.2f}"


def simulate_handicap_table(
    player_a: str,
    player_b: str,
    p1_hold: float,
    p2_hold: float,
    n_sims: int,
    seed: int,
) -> pd.DataFrame:
    """
    Simulates cover probability for Player A on each handicap line.
    Player B's opposite line is derived as 1 - Player A cover probability.
    """
    random.seed(seed)
    cfg = MatchConfig(best_of_sets=3)
    lines = np.arange(-4.5, 5.0, 0.5)
    rows = []

    for line in lines:
        p_a = handicap_cover_prob_mc(
            p1_hold=p1_hold,
            p2_hold=p2_hold,
            line=float(line),
            cfg=cfg,
            n_sims=int(n_sims),
        )
        p_b = 1.0 - p_a

        rows.append(
            {
                "Line": f"{line:+.1f}",
                f"{player_a} cover %": p_a,
                f"{player_a} fair odds": fair_odds(p_a),
                f"{player_b} opposite line": f"{-line:+.1f}",
                f"{player_b} cover %": p_b,
                f"{player_b} fair odds": fair_odds(p_b),
            }
        )

    out = pd.DataFrame(rows)
    return out


def display_table(df: pd.DataFrame, player_a: str, player_b: str) -> None:
    styled = df.copy()
    for col in [f"{player_a} cover %", f"{player_b} cover %"]:
        styled[col] = styled[col].map(lambda x: f"{x:.1%}")
    for col in [f"{player_a} fair odds", f"{player_b} fair odds"]:
        styled[col] = styled[col].map(format_decimal_odds)

    st.dataframe(styled, use_container_width=True, hide_index=True)


st.title("🎾 WTA Handicap Fair Value Model")
st.caption("Upload match data, select two players, choose a surface, and generate fair odds for game handicaps.")

with st.sidebar:
    st.header("Inputs")
    uploaded_file = st.file_uploader("Upload WTA match CSV", type=["csv"])
    st.divider()
    st.caption("The CSV is uploaded into the app session only. It does not need to live in GitHub.")

if uploaded_file is None:
    st.info("Upload your WTA season CSV to start.")
    st.stop()

raw_df = read_uploaded_csv(uploaded_file)
missing = validate_columns(raw_df)
if missing:
    st.error("Your CSV is missing required columns:")
    st.write(missing)
    st.stop()

agg = build_stats(raw_df)
players = available_players(raw_df)
surfaces = available_surfaces(raw_df)
seasons = sorted(raw_df["season_year"].dropna().astype(int).unique(), reverse=True)

with st.sidebar:
    season = st.selectbox("Season", seasons, index=0)
    surface = st.selectbox("Surface", surfaces, index=0)

    player_a = st.selectbox("Player A", players, index=0)
    default_b_index = 1 if len(players) > 1 else 0
    player_b = st.selectbox("Player B", players, index=default_b_index)

    n_sims = st.slider(
        "Monte Carlo simulations",
        min_value=5_000,
        max_value=100_000,
        value=50_000,
        step=5_000,
    )
    seed = st.number_input("Random seed", min_value=1, max_value=999_999, value=42, step=1)
    run_button = st.button("Run model", type="primary")

if player_a == player_b:
    st.warning("Select two different players.")
    st.stop()

try:
    profile_a = get_profile(agg, player_a, surface, int(season))
    profile_b = get_profile(agg, player_b, surface, int(season))
except ValueError as exc:
    st.warning(str(exc))
    st.stop()

p1 = build_hold_return_profile(profile_a)
p2 = build_hold_return_profile(profile_b)

left, right = st.columns(2)
with left:
    st.subheader(player_a)
    st.metric("Matches in sample", profile_a["matches"])
    st.metric("Service points won", f"{profile_a['srv_pts_won']:.1%}")
    st.metric("Estimated hold %", f"{p1['hold']:.1%}")

with right:
    st.subheader(player_b)
    st.metric("Matches in sample", profile_b["matches"])
    st.metric("Service points won", f"{profile_b['srv_pts_won']:.1%}")
    st.metric("Estimated hold %", f"{p2['hold']:.1%}")

if run_button:
    with st.spinner("Running Monte Carlo simulation..."):
        results = simulate_handicap_table(
            player_a=player_a,
            player_b=player_b,
            p1_hold=float(p1["hold"]),
            p2_hold=float(p2["hold"]),
            n_sims=int(n_sims),
            seed=int(seed),
        )

    st.subheader("Fair handicap odds")
    st.caption(
        f"Player A lines are shown from -4.5 to +4.5. "
        f"Player B is shown on the opposite side of the same handicap."
    )
    display_table(results, player_a, player_b)

    csv = results.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv,
        file_name=f"{player_a}_vs_{player_b}_handicap_fair_odds.csv".replace(" ", "_"),
        mime="text/csv",
    )
else:
    st.info("Choose players and click **Run model**.")
