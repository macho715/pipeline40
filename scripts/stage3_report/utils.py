import re
import pandas as pd

SYNONYMS = {
    # collapse double spaces
    "AAA  Storage": "AAA Storage",
    "site  handling": "site handling",
}

def normalize_columns(cols):
    # compress whitespace and strip
    return (
        pd.Index(cols)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

def apply_column_synonyms(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    current = set(df.columns)
    for k, v in SYNONYMS.items():
        if k in current and v not in current:
            rename_map[k] = v
    if rename_map:
        df = df.rename(columns=rename_map)
    return df