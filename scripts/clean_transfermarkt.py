"""
Step 3b - Clean the Transfermarkt player data.

- Keeps only players active in 2024 or 2025 (removes retired players)
- Keeps the 6 columns needed, plus last_season for reference
- Adds birth_year so players can be matched to FBref (name + birth year)

Saves to clean-data/transfermarkt_clean.csv (UTF-8, accents kept).

Run from the project folder:  python scripts/clean_transfermarkt.py
"""
import pandas as pd

RAW = "raw-data/players.csv"
OUT = "clean-data/transfermarkt_clean.csv"

KEEP = [
    "name",
    "date_of_birth",
    "position",
    "sub_position",        # e.g. "Attacking Midfield"
    "current_club_name",
    "market_value_in_eur",
    "last_season",
]

df = pd.read_csv(RAW, encoding="utf-8")
print(f"Raw file: {df.shape[0]} rows, {df.shape[1]} columns")

# 1. Only players active recently
df = df[df["last_season"].isin([2024, 2025])]
print(f"After keeping 2024/2025 players: {len(df)} rows")

# 2. Only the columns we need
df = df[KEEP].copy()

# 3. Add birth year (for matching with FBref's 'Born' column)
df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], errors="coerce").dt.date
df["birth_year"] = pd.to_datetime(df["date_of_birth"]).dt.year.astype("Int64")

df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Clean file: {df.shape[0]} rows, {df.shape[1]} columns -> {OUT}")
