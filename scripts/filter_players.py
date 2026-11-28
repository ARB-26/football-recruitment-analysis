"""
Step 6 - Filter players to the brief.

Keeps only players who:
1. are 25 or under
2. played 900+ minutes
3. are worth under £70m
4. play Attacking Midfield or Central Midfield (Transfermarkt position)

Saves them to clean-data/filtered.csv

Run from the project folder:  python scripts/filter_players.py
"""
import pandas as pd

IN = "clean-data/merged.csv"
OUT = "clean-data/filtered.csv"

# The rules from the brief - change these to try different filters
MAX_AGE = 25
MIN_MINUTES = 900
MAX_VALUE_GBP_M = 100
POSITIONS = ["Attacking Midfield", "Central Midfield"]

df = pd.read_csv(IN, encoding="utf-8-sig")
print(f"Start: {len(df)} players")

df = df[df["Age"] <= MAX_AGE]
print(f"After age {MAX_AGE} or under: {len(df)}")

df = df[df["Min"] >= MIN_MINUTES]
print(f"After {MIN_MINUTES}+ minutes: {len(df)}")

df = df[df["market_value_gbp_m"] < MAX_VALUE_GBP_M]
print(f"After under £{MAX_VALUE_GBP_M}m: {len(df)}")

df = df[df["tm_position"].isin(POSITIONS)]
print(f"After position filter: {len(df)}")

df.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"Saved -> {OUT}")

# Save a SQL-friendly copy: simple lowercase names, only the columns needed
SQL_COLUMNS = {
    "Player": "player",
    "Squad": "club",
    "Comp": "league",
    "Age": "age",
    "Min": "minutes",
    "tm_position": "position",
    "market_value_gbp_m": "value_gbp_m",
    "KP_p90": "kp_p90",
    "TB_p90": "tb_p90",
    "PrgP_p90": "prgp_p90",
    "xAG_p90": "xag_p90",
    "Tkl+Int_p90": "tklint_p90",
}
sql_df = df[list(SQL_COLUMNS)].rename(columns=SQL_COLUMNS)
sql_df.to_csv("clean-data/players_for_sql.csv", index=False, encoding="utf-8")
print("Saved -> clean-data/players_for_sql.csv")