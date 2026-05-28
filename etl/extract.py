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


def run():
    print("=== EXTRACCIÓN ===")
    df_inorg = load_inorganicos()
    df_org = load_organicos()
    df_gen = load_generacion()

    df_inorg.to_csv(PROCESSED_DIR / "inorganicos_clean.csv", index=False, encoding="utf-8")
    df_org.to_csv(PROCESSED_DIR / "organicos_clean.csv", index=False, encoding="utf-8")
    df_gen.to_csv(PROCESSED_DIR / "generacion_clean.csv", index=False, encoding="utf-8")
    print("  Archivos guardados en data/processed/")
    return df_inorg, df_org, df_gen


if __name__ == "__main__":
    run()
