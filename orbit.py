"""
orbit.py — optional CLI batch runner.
Not required for normal use (the app asks you to type everything in),
but handy if you ever want to regenerate images from data_log.csv directly.

Usage: python3 orbit.py
"""

from orbit_core import load_data, draw_black_hole, draw_constellation, save_combined

CSV_PATH = "data_log.csv"

df = load_data(CSV_PATH)
print(df)
print(f"Loaded {len(df)} days of data")

fig1 = draw_black_hole(df)
fig1.savefig("black_hole.png", dpi=150, facecolor="black")
print("Saved black_hole.png")

fig2 = draw_constellation(df)
fig2.savefig("constellation.png", dpi=150, facecolor="black")
print("Saved constellation.png")

save_combined("black_hole.png", "constellation.png", "combined.png")
print("Saved combined.png")
