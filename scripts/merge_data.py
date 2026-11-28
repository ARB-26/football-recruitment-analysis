"""
Step 4 - Merge FBref stats with Transfermarkt market values.

1. Combines players who played for two clubs in 2024/25 into one row
   (stats added together, so minutes and totals are for the whole season)
2. Works out the per-90 stats from the brief
3. Matches each player to Transfermarkt on name + birth year
   - accents/case ignored (Ødegaard = odegaard)
   - NAME_FIXES handles nicknames/spellings that differ between sites
   - if two Transfermarkt players share a name + birth year (e.g. two
     "Vitinha"s born 2000), the one at the matching club is used
4. Converts market value from EUR to GBP

Saves clean-data/merged.csv and clean-data/unmatched.csv (players with
no market value, so you can check them).

Run from the project folder:  python scripts/merge_data.py
"""
import unicodedata
import pandas as pd

FBREF = "clean-data/fbref_clean.csv"
TM = "clean-data/transfermarkt_clean.csv"
OUT = "clean-data/merged.csv"
UNMATCHED = "clean-data/unmatched.csv"

EUR_TO_GBP = 0.85  # approximate exchange rate - update if needed

# FBref name -> Transfermarkt name (found by checking unmatched players)
NAME_FIXES = {
    "Alfon": "Alfon González",
    "Antoniu": "Antoniu Roca",
    "Domingos André Ribeiro Almeida": "André Almeida",
    "Elif Elmas": "Eljif Elmas",
    "Faustino Anjorin": "Tino Anjorin",
    "Hamed Junior Traorè": "Hamed Traoré",
    "Javier Guerra": "Javi Guerra",
    "Jeong Woo-yeong": "Woo-yeong Jeong",
    "Jofre": "Jofre Carreras",
    "José Luis García Vayá": "Pepelu",
    "Lee Kang-in": "Kang-in Lee",
    "Manuel Ugarte Ribeiro": "Manuel Ugarte",
    "Michel Ndary Adopo": "Michel Adopo",
    "Mikael Ellertsson": "Mikael Egill Ellertsson",
    "Nicolás Paz": "Nico Paz",
    "Peque": "Peque Fernández",
    "Pierre Ekwah Elimby": "Pierre Ekwah",
    "Roberto Navarro": "Robert Navarro",
    "Sávio": "Savinho",
    "Urko González": "Urko González de Zárate",
    "Valentin Atangana Edoa": "Valentin Atangana",
    "Waren Kamanzi": "Warren Kamanzi",
    "Yehor Yarmoliuk": "Yegor Yarmolyuk",
    "Yeremi Pino": "Yéremy Pino",
    "Þórir Jóhann Helgason": "Thórir Jóhann Helgason",
}

# Players with no market value in Transfermarkt - filled in by hand (EUR)
MANUAL_VALUES = {
    "Seydouba Cissé": 2_900_000,
    "Issa Doumbia": 7_700_000,
    "Elias Saad": 3_900_000,
}

# Different players who share a name AND birth year in FBref - keep them
# separate instead of combining them as one two-club season
SAME_NAME_DIFFERENT_PLAYERS = {"Vitinha"}  # PSG midfielder vs Genoa striker

STATS = ["KP", "TB", "PrgP", "xAG", "Tkl+Int"]


def simplify(text):
    """Lower case, no accents, no hyphens - so names match across sites."""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("ø", "o").replace("Ø", "o").replace("-", " ")
    return text.lower().strip()


# ---------- 1. FBref: one row per player ----------
fb = pd.read_csv(FBREF, encoding="utf-8-sig")
fb["Born"] = fb["Born"].astype("Int64")
fb["player_id"] = fb["Player"]
clash = fb["Player"].isin(SAME_NAME_DIFFERENT_PLAYERS)
fb.loc[clash, "player_id"] = fb["Player"] + " (" + fb["Squad"] + ")"

fb = (
    fb.groupby(["player_id", "Born"], as_index=False)
    .agg(
        Player=("Player", "first"),
        Nation=("Nation", "first"),
        Pos=("Pos", lambda s: ",".join(sorted(set(",".join(s).split(","))))),
        Squad=("Squad", lambda s: " / ".join(s)),
        Comp=("Comp", lambda s: " / ".join(s)),
        Age=("Age", "first"),
        Min=("Min", "sum"),
        **{col: (col, "sum") for col in STATS},
    )
)
print(f"FBref: {len(fb)} players (after combining two-club seasons)")

# ---------- 2. Per-90 stats ----------
fb["90s"] = fb["Min"] / 90
for col in STATS:
    fb[f"{col}_p90"] = (fb[col] / fb["90s"]).round(2)

# ---------- 3. Match to Transfermarkt ----------
tm = pd.read_csv(TM, encoding="utf-8-sig")
tm["birth_year"] = tm["birth_year"].astype("Int64")
tm["key"] = tm["name"].map(simplify) + "|" + tm["birth_year"].astype(str)

fb["tm_name"] = fb["Player"].map(NAME_FIXES).fillna(fb["Player"])
fb["key"] = fb["tm_name"].map(simplify) + "|" + fb["Born"].astype(str)

merged = fb.merge(
    tm[["key", "name", "sub_position", "current_club_name", "market_value_in_eur"]],
    on="key",
    how="left",
)

# Same name + birth year twice in Transfermarkt: keep the matching club
def club_matches(row):
    if pd.isna(row["current_club_name"]):
        return False
    fb_words = set(simplify(row["Squad"]).replace("/", " ").split())
    tm_words = set(simplify(row["current_club_name"]).split())
    return len(fb_words & tm_words) > 0

merged["club_match"] = merged.apply(club_matches, axis=1)
merged = (
    merged.sort_values(["club_match", "market_value_in_eur"], ascending=False)
    .drop_duplicates(subset=["player_id", "Born"])
    .sort_values("Player")
)


# Fill in blank market values from MANUAL_VALUES
merged["market_value_in_eur"] = merged["market_value_in_eur"].fillna(
    merged["Player"].map(MANUAL_VALUES)
)
# ---------- 4. Tidy up ----------
merged["market_value_gbp_m"] = (merged["market_value_in_eur"] * EUR_TO_GBP / 1e6).round(1)
merged = merged.rename(columns={"sub_position": "tm_position"})
merged = merged.drop(columns=["player_id", "key", "tm_name", "name", "club_match", "current_club_name"])

matched = merged["market_value_in_eur"].notna()
print(f"Matched to a market value: {matched.sum()} of {len(merged)} ({matched.mean():.0%})")

merged.to_csv(OUT, index=False, encoding="utf-8-sig")
merged[~matched][["Player", "Born", "Squad", "Pos", "Min"]].to_csv(
    UNMATCHED, index=False, encoding="utf-8-sig"
)
print(f"Saved -> {OUT}  (unmatched list -> {UNMATCHED})")
