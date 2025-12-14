import pandas as pd

def coerce_numeric(series: pd.Series) -> pd.Series:
    """Convierte una columna a numérico de forma robusta (quita comas, $)"""
    s = series.astype(str).str.replace(",", "", regex=False)
    s = s.str.replace("$", "", regex=False)
    return pd.to_numeric(s, errors="coerce")

def compare_employees_hypothesis(
    df_imss: pd.DataFrame,
    df_gov: pd.DataFrame,
    rfc_imss: str,
    rfc_gov: str,
    imss_employees_col: str,
    gov_candidate_col: str,
    normalize_key_fn,
):
    """
    Une por RFC normalizado y compara:
    IMSS[NO. EMPLEADOS] vs Gobierno[Costo Promedio/Num.]
    (hipótesis: equivalentes)
    """

    imss = df_imss.copy()
    gov = df_gov.copy()

    imss["_rfc"] = normalize_key_fn(imss[rfc_imss])
    gov["_rfc"] = normalize_key_fn(gov[rfc_gov])

    imss["_imss_emp"] = coerce_numeric(imss[imss_employees_col])
    gov["_gov_candidate"] = coerce_numeric(gov[gov_candidate_col])

    # join many-to-many si hay duplicados por RFC; luego lo atendemos
    merged = imss.merge(
        gov,
        on="_rfc",
        how="inner",
        suffixes=("_imss", "_gov")
    )

    # métricas básicas
    valid = merged.dropna(subset=["_imss_emp", "_gov_candidate"]).copy()
    valid["abs_diff"] = (valid["_imss_emp"] - valid["_gov_candidate"]).abs()

    # % diff (evitar división por cero)
    denom = valid["_imss_emp"].replace({0: pd.NA})
    valid["pct_diff"] = (valid["abs_diff"] / denom) * 100

    summary = {
        "matches_rfc_inner_join_rows": int(len(merged)),
        "matches_valid_numeric_rows": int(len(valid)),
        "imss_emp_min": float(valid["_imss_emp"].min()) if len(valid) else None,
        "imss_emp_max": float(valid["_imss_emp"].max()) if len(valid) else None,
        "gov_candidate_min": float(valid["_gov_candidate"].min()) if len(valid) else None,
        "gov_candidate_max": float(valid["_gov_candidate"].max()) if len(valid) else None,
        "corr_pearson": float(valid[["_imss_emp", "_gov_candidate"]].corr().iloc[0,1]) if len(valid) > 2 else None,
        "median_abs_diff": float(valid["abs_diff"].median()) if len(valid) else None,
        "median_pct_diff": float(valid["pct_diff"].median()) if len(valid) else None,
        "pct_exact_equal": float((valid["_imss_emp"] == valid["_gov_candidate"]).mean() * 100) if len(valid) else None,
        "pct_gov_candidate_integer_like": float((valid["_gov_candidate"] % 1 == 0).mean() * 100) if len(valid) else None,
    }

    # Top casos raros
    top_abs = valid.sort_values("abs_diff", ascending=False).head(20)
    top_pct = valid.sort_values("pct_diff", ascending=False).head(20)

    return {
        "merged": merged,
        "valid": valid,
        "summary": summary,
        "top_abs_diff": top_abs,
        "top_pct_diff": top_pct,
    }
