import pandas as pd
import re

def normalize_key(series: pd.Series) -> pd.Series:
    
    s = series.astype(str).str.upper().str.strip()
    s = s.str.replace(r"\s+", "", regex=True)
    s = s.str.replace(r"[^A-Z0-9]", "", regex=True)
    # opcional: convierte "NAN"/"NONE" en NA
    s = s.replace({"NAN": pd.NA, "NONE": pd.NA, "": pd.NA})
    return s



def compute_overlap(
    df_imss: pd.DataFrame,
    df_gov: pd.DataFrame,
    key_imss: str,
    key_gov: str
):
    """
    Calcula overlaps y diferencias entre dos datasets.

    Returns:
        dict con:
            - both
            - only_imss
            - only_gov
            - metrics
    """

    # Copias defensivas
    imss = df_imss.copy()
    gov = df_gov.copy()

    # Normalizar claves
    imss["_key_norm"] = normalize_key(imss[key_imss])
    gov["_key_norm"] = normalize_key(gov[key_gov])

    # Sets de claves
    keys_imss = set(imss["_key_norm"].dropna())
    keys_gov = set(gov["_key_norm"].dropna())

    keys_both = keys_imss & keys_gov
    keys_only_imss = keys_imss - keys_gov
    keys_only_gov = keys_gov - keys_imss

    # Subsets
    df_both_imss = imss[imss["_key_norm"].isin(keys_both)]
    df_both_gov = gov[gov["_key_norm"].isin(keys_both)]

    df_only_imss = imss[imss["_key_norm"].isin(keys_only_imss)]
    df_only_gov = gov[gov["_key_norm"].isin(keys_only_gov)]

    # Métricas
    metrics = {
        "total_imss": len(imss),
        "total_gobierno": len(gov),
        "en_ambos": len(keys_both),
        "solo_imss": len(keys_only_imss),
        "solo_gobierno": len(keys_only_gov),
        "overlap_pct_imss": round(len(keys_both) / len(keys_imss) * 100, 2) if keys_imss else 0,
        "overlap_pct_gobierno": round(len(keys_both) / len(keys_gov) * 100, 2) if keys_gov else 0,
    }

    return {
        "both": {
            "imss": df_both_imss,
            "gobierno": df_both_gov
        },
        "only_imss": df_only_imss,
        "only_gobierno": df_only_gov,
        "metrics": metrics
    }
