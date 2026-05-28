# Datamart — Residuos Sólidos Perú 2019–2024

Datamart analítico sobre valorización y generación de residuos sólidos a nivel distrital en el Perú, construido a partir de datos del MINAM / SIGERSOL.

## Cobertura

| Dataset | Filas | Período |
|---|---|---|
| Valorización inorgánica | 11 310 | 2019–2024 |
| Valorización orgánica | 11 310 | 2019–2024 |
| Generación municipal | 11 310 | 2019–2024 |
| **Distritos** | **1 891** | — |

## Estructura del repositorio

```
datamart-residuos/
├── data/
│   ├── raw/                   # Archivos originales (CSV / XLSX)
│   ├── processed/             # Datos limpios intermedios (generado por ETL)
│   └── marts/                 # Tablas finales (Parquet + DuckDB)
│       ├── dim_tiempo.parquet
│       ├── dim_geografica.parquet
│       ├── dim_municipio.parquet
│       ├── dim_residuo.parquet
│       ├── fact_valorizacion.parquet
│       ├── fact_generacion.parquet
│       └── datamart_residuos.duckdb
├── etl/
│   ├── extract.py             # Carga y normaliza archivos raw
│   ├── transform.py           # Construye dimensiones y tablas de hechos
│   └── load.py                # Carga a DuckDB y genera reporte de calidad
├── tests/
│   └── test_marts.py          # Pruebas de integridad referencial y calidad
├── docs/
│   └── diccionario_datos.md   # Diccionario completo de columnas
├── .github/workflows/
│   └── etl.yml                # CI/CD — ejecuta pipeline en cada push
├── run_pipeline.py            # Punto de entrada único del pipeline
├── requirements.txt
└── .gitignore
```

## Cómo usar

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar el pipeline completo
```bash
python run_pipeline.py
```
Esto genera todos los archivos en `data/processed/` y `data/marts/`.

### 3. Correr los tests
```bash
pytest tests/ -v
```

### 4. Consultar el datamart con DuckDB
```python
import duckdb
con = duckdb.connect("data/marts/datamart_residuos.duckdb", read_only=True)

# Ejemplo: tasa de valorización orgánica por departamento en 2024
con.execute("""
    SELECT g.departamento,
           ROUND(AVG(v.tasa_valorizacion_pct), 2) AS tasa_promedio
    FROM fact_valorizacion v
    JOIN dim_geografica g USING (ubigeo)
    WHERE v.anio = 2024 AND v.tipo_residuo = 'ORGANICO'
    GROUP BY 1 ORDER BY 2 DESC
""").df()
```

También puedes leer directamente los Parquet con pandas:
```python
import pandas as pd
df = pd.read_parquet("data/marts/fact_valorizacion.parquet")
```

## Modelo dimensional

Ver [`docs/diccionario_datos.md`](docs/diccionario_datos.md) para el detalle completo.

## Fuente de datos

- MINAM — Sistema de Información para la Gestión de Residuos Sólidos (SIGERSOL)
- Datos abiertos: [datosabiertos.gob.pe](https://www.datosabiertos.gob.pe)
