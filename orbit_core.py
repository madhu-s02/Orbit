"""
orbit_core.py — shared drawing logic for ORBIT.
Black Hole: time lost to screen/Instagram, pulled inward and consumed.
Constellation: time given to a habit, growing into a connected pattern.

Pure Python (matplotlib + pandas + numpy). No HTML/CSS/JS.
Import this from orbit.py (CLI) or app.py (Streamlit) — draw functions
return the matplotlib Figure so callers can save it, show it, or embed it.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image

plt.rcParams["font.family"] = "DejaVu Sans"


def load_data(path):
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


def filter_period(df, period="all"):
    """period: 'week' (last 7 days), 'month' (last 30 days), or 'all'."""
    if period == "all" or "date" not in df.columns or len(df) == 0:
        return df
    cutoff_days = 7 if period == "week" else 30
    cutoff = df["date"].max() - pd.Timedelta(days=cutoff_days - 1)
    return df[df["date"] >= cutoff].reset_index(drop=True)


def draw_starfield(ax, n=250, xlim=(0, 10), ylim=(0, 10), seed=None):
    """Ambient background stars — tiny white dots at random positions/brightness."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(xlim[0], xlim[1], n)
    ys = rng.uniform(ylim[0], ylim[1], n)
    sizes = rng.uniform(0.5, 4, n)
    alphas = rng.uniform(0.2, 0.9, n)
    for x, y, s, a in zip(xs, ys, sizes, alphas):
        ax.scatter(x, y, s=s, color="white", alpha=a, zorder=0, linewidths=0)


# ---------- BLACK HOLE (brutal side) ----------
def draw_black_hole(df, seed=7, period_label="All Time"):
    """Returns a matplotlib Figure. Caller decides whether to savefig / st.pyplot."""
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=(9, 9), facecolor="black")
    ax.set_facecolor("black")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    draw_starfield(ax, n=300, seed=seed)

    center = (5, 5)
    ring_colors = ["#000000", "#1a0500", "#3d0f00", "#7a1f00", "#c94b00", "#ff7b00"]
    ring_radii = [0.5, 1.0, 1.6, 2.3, 3.1, 4.0]
    for r, c in zip(reversed(ring_radii), reversed(ring_colors)):
        ax.add_patch(patches.Circle(center, r, color=c, alpha=0.35, zorder=1))
    ax.add_patch(patches.Circle(center, 0.45, color="black", zorder=2))

    total_minutes = df["total_screentime_minutes"].values
    max_time = total_minutes.max() if len(total_minutes) else 1
    n = len(df)

    total_wasted_hours = total_minutes.sum() / 60
    ig_hours = df["instagram_minutes"].sum() / 60

    for i, minutes in enumerate(total_minutes):
        angle = i * 2.4 + rng.uniform(-0.2, 0.2)
        progress = i / max(n - 1, 1)
        dist = 4.3 - progress * 3.5
        x = center[0] + dist * np.cos(angle)
        y = center[1] + dist * np.sin(angle)

        weight = minutes / max_time
        size = 20 + weight * 220
        color = plt.cm.autumn(1 - weight * 0.7)

        ax.scatter(x, y, s=size, color=color, alpha=0.85, zorder=3, edgecolors="none")
        ax.plot([x, center[0]], [y, center[1]], color=color, alpha=0.12,
                linewidth=1, zorder=1)

    books_lost = round(total_wasted_hours / 6, 1)
    ax.text(5, 9.1, "THE BLACK HOLE", color="white", fontsize=22,
            ha="center", fontweight="bold", family="monospace")
    ax.text(5, 8.55, f"{period_label} · {n} day{'s' if n != 1 else ''} tracked",
            color="#999999", fontsize=11, ha="center")

    stat_text = (
        f"{total_wasted_hours:.1f} hours consumed\n"
        f"{ig_hours:.1f} of those hours on Instagram alone\n"
        f"≈ {books_lost} books you could have finished"
    )
    ax.text(5, 0.9, stat_text, color="#ffb066", fontsize=12, ha="center", va="center",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="black",
                       edgecolor="#ff7b00", linewidth=1, alpha=0.85))

    fig.tight_layout()
    return fig


# ---------- CONSTELLATION (victory side) ----------
def draw_constellation(df, seed=7, period_label="All Time", habit_name="your habit"):
    rng = np.random.default_rng(seed)
    fig, ax = plt.subplots(figsize=(9, 9), facecolor="black")
    ax.set_facecolor("black")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    draw_starfield(ax, n=300, seed=seed)

    habit_days = df[df["habit_done"] == "yes"].reset_index()
    n_habit = len(habit_days)
    total_habit_hours = df["habit_minutes"].sum() / 60
    streak_days = n_habit

    positions = []
    for i, row in habit_days.iterrows():
        t = i / max(n_habit - 1, 1)
        x = 1.2 + t * 7.6 + rng.uniform(-0.15, 0.15)
        y = 2.5 + t * 5.0 + np.sin(t * 3.2) * 0.6 + rng.uniform(-0.1, 0.1)
        positions.append((x, y))

    for i in range(len(positions) - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        ax.plot([x1, x2], [y1, y2], color="#7fd8ff", alpha=0.5, linewidth=1.2, zorder=1)

    star_cmap = LinearSegmentedColormap.from_list(
        "star", ["#9fd3ff", "#ffffff", "#ffd27f", "#ffb347"]
    )

    max_minutes = habit_days["habit_minutes"].max() if n_habit else 1
    for (x, y), minutes in zip(positions, habit_days["habit_minutes"]):
        weight = minutes / max_minutes
        size = 70 + weight * 280
        color = star_cmap(weight)
        ax.scatter(x, y, s=size * 4.5, color=color, alpha=0.12, zorder=2, linewidths=0)
        ax.scatter(x, y, s=size * 2.2, color=color, alpha=0.25, zorder=2, linewidths=0)
        ax.scatter(x, y, s=size, color=color, alpha=0.95, zorder=3,
                   edgecolors="white", linewidths=0.4)

    ax.text(5, 9.1, "THE CONSTELLATION", color="white", fontsize=22,
            ha="center", fontweight="bold", family="monospace")
    ax.text(5, 8.55,
            f"{period_label} · {streak_days} day{'s' if streak_days != 1 else ''} "
            f"{habit_name} won",
            color="#999999", fontsize=11, ha="center")

    stat_text = (
        f"{total_habit_hours:.1f} hours invested in {habit_name}\n"
        f"{streak_days} star{'s' if streak_days != 1 else ''} formed in this streak\n"
        f"every star is a day you chose {habit_name} over the scroll"
    )
    ax.text(5, 0.9, stat_text, color="#bfe9ff", fontsize=12, ha="center", va="center",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.6", facecolor="black",
                       edgecolor="#7fd8ff", linewidth=1, alpha=0.85))

    fig.tight_layout()
    return fig


# ---------- COMBINED SIDE-BY-SIDE ----------
def save_combined(black_hole_path, constellation_path, out_path="combined.png",
                   gap=24):
    """Stitches the two already-saved PNGs side by side with a thin divider."""
    left = Image.open(black_hole_path)
    right = Image.open(constellation_path)
    h = max(left.height, right.height)
    w = left.width + right.width + gap
    canvas = Image.new("RGB", (w, h), color=(0, 0, 0))
    canvas.paste(left, (0, 0))
    canvas.paste(right, (left.width + gap, 0))
    canvas.save(out_path)
    return out_path
