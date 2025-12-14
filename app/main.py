import streamlit as st
import pandas as pd

from matching.overlap import compute_overlap
from analysis.workforce import compare_employees_hypothesis
from matching.overlap import normalize_key  
from profiling.quality import profile_dataset



# --------------------------------------------------
# Configuración general
# --------------------------------------------------
st.set_page_config(
    page_title="Data Compare Platform",
    layout="wide"
)

st.title("📊 Data Compare Platform")
st.subheader("Diagnóstico y comparación de bases de datos empresariales")

st.markdown(
    """
    Esta herramienta permite cargar dos bases de datos (IMSS y Gobierno),
    analizar su estado general y preparar la comparación entre ambas.
    """
)

# --------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------
def load_file(uploaded_file):
    """Carga CSV o Excel y devuelve un DataFrame"""
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    elif filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file, engine="openpyxl")

    elif filename.endswith(".xls"):
        return pd.read_excel(uploaded_file, engine="xlrd")

    else:
        st.error("Formato no soportado")
        return None



def dataset_summary(df: pd.DataFrame):
    """Resumen básico del dataset"""
    return {
        "Registros": df.shape[0],
        "Columnas": df.shape[1],
        "Valores nulos totales": int(df.isna().sum().sum())
    }


# --------------------------------------------------
# Carga de archivos
# --------------------------------------------------
st.header("1️⃣ Carga de bases de datos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Base IMSS")
    imss_file = st.file_uploader(
        "Sube la base del IMSS (CSV o Excel)",
        type=["csv", "xls", "xlsx"],
        key="imss"
    )

with col2:
    st.markdown("### Base Gobierno")
    gov_file = st.file_uploader(
        "Sube la base del Gobierno (CSV o Excel)",
        type=["csv", "xls", "xlsx"],
        key="gov"
    )

# --------------------------------------------------
# Procesamiento y preview
# --------------------------------------------------
if imss_file and gov_file:
    df_imss = load_file(imss_file)
    df_gov = load_file(gov_file)

    if df_imss is not None and df_gov is not None:
        st.success("Archivos cargados correctamente ✅")

        st.header("2️⃣ Vista previa y diagnóstico")

        tab1, tab2 = st.tabs(["IMSS", "Gobierno"])

        with tab1:
            st.markdown("#### Vista previa IMSS")
            st.dataframe(df_imss.head(20), use_container_width=True)

            st.markdown("#### Resumen IMSS")
            st.json(dataset_summary(df_imss))

        with tab2:
            st.markdown("#### Vista previa Gobierno")
            st.dataframe(df_gov.head(20), use_container_width=True)

            st.markdown("#### Resumen Gobierno")
            st.json(dataset_summary(df_gov))

        # --------------------------------------------------
        # Selección de clave de comparación
        # --------------------------------------------------
        st.header("3️⃣ Configuración de comparación")

        st.markdown(
            """
            Selecciona la columna que servirá como **identificador común**
            entre ambas bases (por ejemplo RFC, razón social normalizada, etc.).
            """
        )

        col_key1, col_key2 = st.columns(2)

        with col_key1:
            key_imss = st.selectbox(
                "Columna clave en IMSS",
                options=df_imss.columns
            )

        with col_key2:
            key_gov = st.selectbox(
                "Columna clave en Gobierno",
                options=df_gov.columns
            )

        st.info(
            f"""
            🔑 Clave seleccionada:
            - IMSS → **{key_imss}**
            - Gobierno → **{key_gov}**

            En el siguiente paso se calcularán overlaps y diferencias usando estas columnas.
            """
        )

        st.markdown("---")
        st.markdown("👉 **Siguiente paso**: análisis de overlaps y métricas comparativas.")

        if st.button("🔍 Calcular overlap"):
            result = compute_overlap(
                df_imss=df_imss,
                df_gov=df_gov,
                key_imss=key_imss,
                key_gov=key_gov
            )

            st.header("4️⃣ Resultados de overlap")

            st.metric("Empresas en ambos", result["metrics"]["en_ambos"])
            st.metric("Solo IMSS", result["metrics"]["solo_imss"])
            st.metric("Solo Gobierno", result["metrics"]["solo_gobierno"])

            st.json(result["metrics"])
            
st.header("4️⃣ Data Profiling y Calidad de Datos")

tab_q1, tab_q2 = st.tabs(["IMSS", "Gobierno"])

with tab_q1:
    st.subheader("Perfil de calidad — IMSS")
    key_imss_profile = st.selectbox(
        "Columna identificadora (opcional)",
        options=["(ninguna)"] + list(df_imss.columns),
        key="profile_imss_key"
    )

    key_imss_profile = None if key_imss_profile == "(ninguna)" else key_imss_profile

    imss_profile = profile_dataset(df_imss, key_col=key_imss_profile)

    st.json(imss_profile["summary"])
    st.dataframe(imss_profile["profile_table"], use_container_width=True)

    if imss_profile["duplicates"]:
        st.markdown("**Duplicados detectados**")
        st.json(imss_profile["duplicates"])

with tab_q2:
    st.subheader("Perfil de calidad — Gobierno")
    key_gov_profile = st.selectbox(
        "Columna identificadora (opcional)",
        options=["(ninguna)"] + list(df_gov.columns),
        key="profile_gov_key"
    )

    key_gov_profile = None if key_gov_profile == "(ninguna)" else key_gov_profile

    gov_profile = profile_dataset(df_gov, key_col=key_gov_profile)

    st.json(gov_profile["summary"])
    st.dataframe(gov_profile["profile_table"], use_container_width=True)

    if gov_profile["duplicates"]:
        st.markdown("**Duplicados detectados**")
        st.json(gov_profile["duplicates"])
