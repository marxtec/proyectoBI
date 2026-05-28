"""
transform.py
Construye las dimensiones y tablas de hechos del datamart.

Modelo dimensional:
  - dim_tiempo       : dimensión tiempo (año)
  - dim_geografica   : dimensión geográfica (ubigeo, distrito, provincia, dpto, región)
  - dim_municipio    : dimensión municipio (tipo, clasificación MEF)
  - dim_residuo      : dimensión tipo de residuo (orgánico / inorgánico)
  - fact_valorizacion: hechos de valorización por distrito y año
  - fact_generacion  : hechos de generación municipal y domiciliaria por distrito y año
"""

import pandas as pd
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
MARTS_DIR = Path(__file__).parent.parent / "data" / "marts"
MARTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _read(filename: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / filename, encoding="utf-8")


# ── Dimensiones ──────────────────────────────────────────────────────────────

def build_dim_tiempo(df_gen: pd.DataFrame) -> pd.DataFrame:
    anios = sorted(df_gen["ANIO"].unique())
    dim = pd.DataFrame({"anio_id": anios, "anio": anios})
    dim["decada"] = (dim["anio"] // 10) * 10
    dim["es_ultimo_anio"] = dim["anio"] == dim["anio"].max()
    print(f"  dim_tiempo: {len(dim)} filas")
    return dim


def build_dim_geografica(df_gen: pd.DataFrame) -> pd.DataFrame:
    cols = ["UBIGEO", "DEPARTAMENTO", "PROVINCIA", "DISTRITO", "REGION_NATURAL"]
    dim = df_gen[cols].drop_duplicates().copy()
    dim.columns = ["ubigeo", "departamento", "provincia", "distrito", "region_natural"]
    dim = dim.sort_values("ubigeo").reset_index(drop=True)
    print(f"  dim_geografica: {len(dim)} filas (distritos únicos)")
    return dim


def build_dim_municipio(df_gen: pd.DataFrame) -> pd.DataFrame:
    cols = ["UBIGEO", "TIPO_MUNICIPALIDAD", "CLASIFICACION_MUNICIPAL_MEF"]
    dim = df_gen[cols].drop_duplicates(subset=["UBIGEO"]).copy()
    dim.columns = ["ubigeo", "tipo_municipalidad", "clasificacion_mef"]
    dim = dim.sort_values("ubigeo").reset_index(drop=True)
    print(f"  dim_municipio: {len(dim)} filas")
    return dim


def build_dim_residuo() -> pd.DataFrame:
    dim = pd.DataFrame({
        "residuo_id": [1, 2],
        "tipo_residuo": ["ORGANICO", "INORGANICO"],
        "descripcion": [
            "Residuos orgánicos valorizables (compostaje, biodigestión, etc.)",
            "Residuos inorgánicos valorizables (reciclaje de papel, plástico, metal, etc.)"
        ]
    })
    print(f"  dim_residuo: {len(dim)} filas")
    return dim


# ── Tablas de hechos ──────────────────────────────────────────────────────────

def build_fact_valorizacion(df_inorg: pd.DataFrame, df_org: pd.DataFrame) -> pd.DataFrame:
    """Consolida valorización orgánica e inorgánica en una sola tabla de hechos."""

    cols_base = ["UBIGEO", "PERIODO", "TIPO_RESIDUO",
                 "POB_TOTAL", "POB_URBANA", "POB_RURAL",
                 "QRESIDUOS_MUN", "QRESIDUOS_VALORIZADO"]

    # Asegurar columnas presentes
    df_inorg = df_inorg[cols_base].copy()
    df_org = df_org[cols_base].copy()

    fact = pd.concat([df_inorg, df_org], ignore_index=True)
    fact.columns = [c.lower() for c in fact.columns]
    fact = fact.rename(columns={"periodo": "anio"})

    # Métricas derivadas
    fact["tasa_valorizacion_pct"] = (
        fact["qresiduos_valorizado"] / fact["qresiduos_mun"].replace(0, pd.NA) * 100
    ).round(4)

    fact = fact.sort_values(["ubigeo", "anio", "tipo_residuo"]).reset_index(drop=True)
    fact.insert(0, "id", range(1, len(fact) + 1))
    print(f"  fact_valorizacion: {len(fact)} filas")
    return fact


def build_fact_generacion(df_gen: pd.DataFrame) -> pd.DataFrame:
    """Tabla de hechos de generación de residuos municipales y domiciliarios."""
    cols = [
        "UBIGEO", "ANIO",
        "POB_TOTAL_INEI", "POB_URBANA_INEI", "POB_RURAL_INEI",
        "GENERACION_PER_CAPITA_DOM",
        "GENERACION_DOM_URBANA_TDIA",
        "GENERACION_DOM_URBANA_TANIO",
        "GENERACION_MUN_TANIO",
        "GENERACION_MUN_TDIA",
        "GENERACION_PER_CAPITA_MUNICIPAL"
    ]
    fact = df_gen[cols].copy()
    fact.columns = [c.lower() for c in fact.columns]

    # Métricas derivadas
    fact["ratio_dom_vs_mun_pct"] = (
        fact["generacion_dom_urbana_tdia"] / fact["generacion_mun_tdia"].replace(0, pd.NA) * 100
    ).round(4)

    fact = fact.sort_values(["ubigeo", "anio"]).reset_index(drop=True)
    fact.insert(0, "id", range(1, len(fact) + 1))
    print(f"  fact_generacion: {len(fact)} filas")
    return fact


# ── Runner ────────────────────────────────────────────────────────────────────

def run():
    print("=== TRANSFORMACIÓN ===")
    df_inorg = _read("inorganicos_clean.csv")
    df_org = _read("organicos_clean.csv")
    df_gen = _read("generacion_clean.csv")

    # Dimensiones
    dim_tiempo = build_dim_tiempo(df_gen)
    dim_geo = build_dim_geografica(df_gen)
    dim_municipio = build_dim_municipio(df_gen)
    dim_residuo = build_dim_residuo()

    # Hechos
    fact_val = build_fact_valorizacion(df_inorg, df_org)
    fact_gen = build_fact_generacion(df_gen)

    # Guardar marts
    dim_tiempo.to_parquet(MARTS_DIR / "dim_tiempo.parquet", index=False)
    dim_geo.to_parquet(MARTS_DIR / "dim_geografica.parquet", index=False)
    dim_municipio.to_parquet(MARTS_DIR / "dim_municipio.parquet", index=False)
    dim_residuo.to_parquet(MARTS_DIR / "dim_residuo.parquet", index=False)
    fact_val.to_parquet(MARTS_DIR / "fact_valorizacion.parquet", index=False)
    fact_gen.to_parquet(MARTS_DIR / "fact_generacion.parquet", index=False)

    # También en CSV para fácil inspección
    dim_tiempo.to_csv(MARTS_DIR / "dim_tiempo.csv", index=False)
    dim_geo.to_csv(MARTS_DIR / "dim_geografica.csv", index=False)
    dim_municipio.to_csv(MARTS_DIR / "dim_municipio.csv", index=False)
    dim_residuo.to_csv(MARTS_DIR / "dim_residuo.csv", index=False)
    fact_val.to_csv(MARTS_DIR / "fact_valorizacion.csv", index=False)
    fact_gen.to_csv(MARTS_DIR / "fact_generacion.csv", index=False)

    print("  Tablas guardadas en data/marts/")
    return dim_tiempo, dim_geo, dim_municipio, dim_residuo, fact_val, fact_gen


if __name__ == "__main__":
    run()
