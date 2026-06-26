"""
extract.py
Carga los archivos raw y los guarda como CSV normalizados en data/processed/
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_inorganicos() -> pd.DataFrame:
    """Carga el dataset de valorización de residuos inorgánicos."""
    path = RAW_DIR / "inorganicos_2019_2024.csv"
    df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    # Normalizar nombre de columna con espacio
    df = df.rename(columns={"QRESIDUOS _VAL_INORGAN": "QRESIDUOS_VAL_INORGAN"})
    df["TIPO_RESIDUO"] = "INORGANICO"
    df = df.rename(columns={"QRESIDUOS_VAL_INORGAN": "QRESIDUOS_VALORIZADO"})
    print(f"  [inorganicos] {len(df)} filas cargadas.")
    return df


def load_organicos() -> pd.DataFrame:
    """Carga el dataset de valorización de residuos orgánicos."""
    path = RAW_DIR / "organicos_2019_2024.xlsx"
    df = pd.read_excel(path)
    df = df.rename(columns={"QRESIDUOS _VAL_ORGAN": "QRESIDUOS_VALORIZADO",
                             "REG_NAT": "REG_NAT"})
    df["TIPO_RESIDUO"] = "ORGANICO"
    print(f"  [organicos] {len(df)} filas cargadas.")
    return df


def load_generacion() -> pd.DataFrame:
    """Carga el dataset de generación anual de residuos."""
    path = RAW_DIR / "generacion_anual_2019_2024.csv"
    df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    # Normalizar columna con espacio
    df = df.rename(columns={"GENERACION_DOM URBANA_TANIO": "GENERACION_DOM_URBANA_TANIO"})
    print(f"  [generacion] {len(df)} filas cargadas.")
    return df


def load_gasto_mantenimiento() -> pd.DataFrame | None:
    """Carga el dataset de gasto en mantenimiento diario del MEF/SIAF."""
    path = RAW_DIR / "Gasto_Mantenimiento_Diario.csv"
    if not path.exists():
        print("  [gasto_mantenimiento] Archivo no encontrado, omitiendo.")
        return None
    df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    df["FUENTE_GASTO"] = "MANTENIMIENTO"
    print(f"  [gasto_mantenimiento] {len(df)} filas cargadas.")
    return df


def load_gasto_cambio_climatico() -> pd.DataFrame | None:
    """Carga el dataset de gasto en cambio climático del MEF/SIAF."""
    path = RAW_DIR / "Gasto_Cambio_Climatico.csv"
    if not path.exists():
        print("  [gasto_cambio_climatico] Archivo no encontrado, omitiendo.")
        return None
    df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    df["FUENTE_GASTO"] = "CAMBIO_CLIMATICO"
    print(f"  [gasto_cambio_climatico] {len(df)} filas cargadas.")
    return df


def run():
    print("=== EXTRACCIÓN ===")
    df_inorg = load_inorganicos()
    df_org = load_organicos()
    df_gen = load_generacion()

    df_inorg.to_csv(PROCESSED_DIR / "inorganicos_clean.csv", index=False, encoding="utf-8")
    df_org.to_csv(PROCESSED_DIR / "organicos_clean.csv", index=False, encoding="utf-8")
    df_gen.to_csv(PROCESSED_DIR / "generacion_clean.csv", index=False, encoding="utf-8")

    df_mant = load_gasto_mantenimiento()
    df_cc = load_gasto_cambio_climatico()
    if df_mant is not None:
        df_mant.to_csv(PROCESSED_DIR / "gasto_mantenimiento_clean.csv", index=False, encoding="utf-8")
    if df_cc is not None:
        df_cc.to_csv(PROCESSED_DIR / "gasto_cambio_climatico_clean.csv", index=False, encoding="utf-8")

    print("  Archivos guardados en data/processed/")
    return df_inorg, df_org, df_gen, df_mant, df_cc


if __name__ == "__main__":
    run()
