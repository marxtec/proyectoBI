# Diccionario de Datos — Datamart Residuos Sólidos

**Fuente:** MINAM / SIGERSOL  
**Cobertura temporal:** 2019 – 2024  
**Granularidad:** Distrital (1 891 distritos del Perú)

---

## Modelo dimensional

```
dim_tiempo ──────────────┐
dim_geografica ───────────┤──── fact_valorizacion
dim_residuo ─────────────┘
dim_geografica ───────────┬──── fact_generacion
dim_tiempo ───────────────┘
dim_municipio ────────────┘
```

---

## Dimensiones

### `dim_tiempo`
| Columna | Tipo | Descripción |
|---|---|---|
| `anio_id` | int | PK — año (igual al año) |
| `anio` | int | Año del período (2019–2024) |
| `decada` | int | Década (ej. 2020) |
| `es_ultimo_anio` | bool | True si es el año más reciente |

---

### `dim_geografica`
| Columna | Tipo | Descripción |
|---|---|---|
| `ubigeo` | int | PK — código de ubigeo INEI |
| `departamento` | str | Nombre del departamento |
| `provincia` | str | Nombre de la provincia |
| `distrito` | str | Nombre del distrito |
| `region_natural` | str | Costa / Sierra / Selva |

---

### `dim_municipio`
| Columna | Tipo | Descripción |
|---|---|---|
| `ubigeo` | int | PK — código de ubigeo INEI |
| `tipo_municipalidad` | str | Provincial / Distrital |
| `clasificacion_mef` | str | Clasificación municipal MEF |

---

### `dim_residuo`
| Columna | Tipo | Descripción |
|---|---|---|
| `residuo_id` | int | PK (1=Orgánico, 2=Inorgánico) |
| `tipo_residuo` | str | ORGANICO / INORGANICO |
| `descripcion` | str | Descripción del tipo |

---

## Tablas de hechos

### `fact_valorizacion`
Valorización de residuos (orgánicos e inorgánicos) a nivel distrital.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | int | PK surrogate |
| `ubigeo` | int | FK → dim_geografica |
| `anio` | int | FK → dim_tiempo |
| `tipo_residuo` | str | FK → dim_residuo |
| `pob_total` | int | Población total del distrito |
| `pob_urbana` | int | Población urbana |
| `pob_rural` | int | Población rural |
| `qresiduos_mun` | float | Residuos municipales generados (t/año) |
| `qresiduos_valorizado` | float | Residuos efectivamente valorizados (t/año) |
| `tasa_valorizacion_pct` | float | `qresiduos_valorizado / qresiduos_mun × 100` |

---

### `fact_generacion`
Generación de residuos domiciliarios y municipales a nivel distrital.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | int | PK surrogate |
| `ubigeo` | int | FK → dim_geografica |
| `anio` | int | FK → dim_tiempo |
| `pob_total_inei` | int | Población total (INEI) |
| `pob_urbana_inei` | int | Población urbana (INEI) |
| `pob_rural_inei` | int | Población rural (INEI) |
| `generacion_per_capita_dom` | float | GPC domiciliaria (kg/hab/día) |
| `generacion_dom_urbana_tdia` | float | Generación domiciliaria urbana (t/día) |
| `generacion_dom_urbana_tanio` | float | Generación domiciliaria urbana (t/año) |
| `generacion_mun_tanio` | float | Generación municipal total (t/año) |
| `generacion_mun_tdia` | float | Generación municipal total (t/día) |
| `generacion_per_capita_municipal` | float | GPC municipal (kg/hab/día) |
| `ratio_dom_vs_mun_pct` | float | `generacion_dom_urbana_tdia / generacion_mun_tdia × 100` |

---

## Consultas de ejemplo

```sql
-- Top 10 distritos con mayor tasa de valorización inorgánica en 2024
SELECT g.distrito, g.departamento, v.tasa_valorizacion_pct
FROM fact_valorizacion v
JOIN dim_geografica g USING (ubigeo)
WHERE v.anio = 2024 AND v.tipo_residuo = 'INORGANICO'
  AND v.tasa_valorizacion_pct IS NOT NULL
ORDER BY v.tasa_valorizacion_pct DESC
LIMIT 10;

-- Generación municipal por región natural y año
SELECT g.region_natural, f.anio,
       SUM(f.generacion_mun_tanio) AS total_residuos_t
FROM fact_generacion f
JOIN dim_geografica g USING (ubigeo)
GROUP BY 1, 2
ORDER BY 1, 2;

-- Evolución de valorización orgánica nacional
SELECT anio,
       SUM(qresiduos_valorizado) AS total_valorizado_t,
       SUM(qresiduos_mun) AS total_generado_t,
       ROUND(SUM(qresiduos_valorizado)/SUM(qresiduos_mun)*100, 2) AS tasa_nacional
FROM fact_valorizacion
WHERE tipo_residuo = 'ORGANICO'
GROUP BY anio ORDER BY anio;
```
