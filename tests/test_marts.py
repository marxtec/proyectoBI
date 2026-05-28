"""
tests/test_marts.py
Pruebas básicas de calidad sobre los marts del datamart.
Ejecutar con:  pytest tests/
"""

import pytest
import pandas as pd
import duckdb
from pathlib import Path

MARTS_DIR = Path(__file__).parent.parent / "data" / "marts"
DB_PATH = MARTS_DIR / "datamart_residuos.duckdb"


@pytest.fixture(scope="module")
def con():
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    yield conn
    conn.close()


class TestDimTiempo:
    def test_rango_anios(self, con):
        r = con.execute("SELECT MIN(anio), MAX(anio) FROM dim_tiempo").fetchone()
        assert r[0] == 2019
        assert r[1] == 2024

    def test_sin_duplicados(self, con):
        total = con.execute("SELECT COUNT(*) FROM dim_tiempo").fetchone()[0]
        unicos = con.execute("SELECT COUNT(DISTINCT anio) FROM dim_tiempo").fetchone()[0]
        assert total == unicos


class TestDimGeografica:
    def test_ubigeos_distintos(self, con):
        """1891 ubigeos únicos (hay filas duplicadas por combinar fuentes)"""
        unicos = con.execute("SELECT COUNT(DISTINCT ubigeo) FROM dim_geografica").fetchone()[0]
        assert unicos == 1891

    def test_sin_nulos_ubigeo(self, con):
        nulos = con.execute("SELECT COUNT(*) FROM dim_geografica WHERE ubigeo IS NULL").fetchone()[0]
        assert nulos == 0


class TestDimResiduos:
    def test_dos_tipos(self, con):
        count = con.execute("SELECT COUNT(*) FROM dim_residuo").fetchone()[0]
        assert count == 2

    def test_tipos_correctos(self, con):
        tipos = {r[0] for r in con.execute("SELECT tipo_residuo FROM dim_residuo").fetchall()}
        assert tipos == {"ORGANICO", "INORGANICO"}


class TestFactValorizacion:
    def test_total_filas(self, con):
        """11310 distritos x 2 tipos = 22620 filas"""
        count = con.execute("SELECT COUNT(*) FROM fact_valorizacion").fetchone()[0]
        assert count == 22620

    def test_tasa_valorizacion_no_negativa(self, con):
        """Tasa no puede ser negativa; puede superar 100 por errores de reporte en origen"""
        negativos = con.execute("""
            SELECT COUNT(*) FROM fact_valorizacion
            WHERE tasa_valorizacion_pct < 0
        """).fetchone()[0]
        assert negativos == 0

    def test_integridad_ubigeos(self, con):
        sin_match = con.execute("""
            SELECT COUNT(*) FROM fact_valorizacion
            WHERE ubigeo NOT IN (SELECT ubigeo FROM dim_geografica)
        """).fetchone()[0]
        assert sin_match == 0

    def test_integridad_anios(self, con):
        sin_match = con.execute("""
            SELECT COUNT(*) FROM fact_valorizacion
            WHERE anio NOT IN (SELECT anio FROM dim_tiempo)
        """).fetchone()[0]
        assert sin_match == 0


class TestFactGeneracion:
    def test_total_filas(self, con):
        """11310 filas (1891 distritos x 6 años)"""
        count = con.execute("SELECT COUNT(*) FROM fact_generacion").fetchone()[0]
        assert count == 11310

    def test_generacion_positiva(self, con):
        negativos = con.execute("""
            SELECT COUNT(*) FROM fact_generacion
            WHERE generacion_mun_tanio < 0
        """).fetchone()[0]
        assert negativos == 0

    def test_integridad_ubigeos(self, con):
        sin_match = con.execute("""
            SELECT COUNT(*) FROM fact_generacion
            WHERE ubigeo NOT IN (SELECT ubigeo FROM dim_geografica)
        """).fetchone()[0]
        assert sin_match == 0
