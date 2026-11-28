"""
Step 3a - Clean the FBref 2024/25 player data.

Keeps only the 14 columns needed for the attacking-midfielder brief
and saves them to clean-data/fbref_clean.csv (UTF-8, so accented
names like Mbappé and Ødegaard stay intact for matching later).

Run from the project folder:  python scripts/clean_fbref.py
"""
import pandas as pd

RAW = "raw-data/players_data-2024_2025.csv"
OUT = "clean-data/fbref_clean.csv"

KEEP = [
    # Who / where
    "Player", "Nation", "Pos", "Squad", "Comp", "Age", "Born",
    # Playing time
    "Min", "90s",
    # Key stats from the brief
    "KP",       # key passes
    "TB",       # through balls
    "PrgP",     # progressive passes
    "xAG",      # expected assisted goals
    "Tkl+Int",  # tackles + interceptions
]

df = pd.read_csv(RAW, encoding="utf-8")
print(f"Raw file: {df.shape[0]} rows, {df.shape[1]} columns")

clean = df[KEEP]

# utf-8-sig adds a marker so Excel also reads the accents correctly
clean.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Clean file: {clean.shape[0]} rows, {clean.shape[1]} columns -> {OUT}")
