import pandas as pd

def profile_dataset(df: pd.DataFrame, key_col: str | None = None):
    """
    Genera un perfil de calidad del dataset.

    Args:
        df: DataFrame a analizar
        key_col: columna identificadora (ej. RFC), opcional

    Returns:
        dict con métricas y tablas de profiling
    """

    total_rows = len(df)

    # ---------------------------
    # Perfil por columna
    # ---------------------------
    profile_rows = []

    for col in df.columns:
        series = df[col]

        n_null = series.isna().sum()
        n_unique = series.nunique(dropna=True)

        profile_rows.append({
            "columna": col,
            "tipo": str(series.dtype),
            "nulos": int(n_null),
            "pct_nulos": round(n_null / total_rows * 100, 2) if total_rows else 0,
            "unicos": int(n_unique),
            "pct_unicos": round(n_unique / total_rows * 100, 2) if total_rows else 0,
            "es_constante": n_unique <= 1,
        })

    profile_df = pd.DataFrame(profile_rows).sort_values(
        by=["pct_nulos", "pct_unicos"],
        ascending=[False, True]
    )

    # ---------------------------
    # Duplicados (si hay key)
    # ---------------------------
    duplicates_info = None
    if key_col and key_col in df.columns:
        dup_mask = df[key_col].duplicated(keep=False)
        duplicates_info = {
            "total_duplicados": int(dup_mask.sum()),
            "pct_duplicados": round(dup_mask.mean() * 100, 2),
            "ejemplos": df.loc[dup_mask, [key_col]].head(10)
        }

    # ---------------------------
    # Resumen general
    # ---------------------------
    summary = {
        "filas": total_rows,
        "columnas": df.shape[1],
        "columnas_con_nulos": int((profile_df["nulos"] > 0).sum()),
        "columnas_constantes": int(profile_df["es_constante"].sum()),
        "columnas_mayor_50pct_nulos": int((profile_df["pct_nulos"] > 50).sum()),
    }

    return {
        "summary": summary,
        "profile_table": profile_df,
        "duplicates": duplicates_info,
    }
