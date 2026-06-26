"""Queries para Dashboard 3 — Gasto Presupuestal."""
from .db import get_con

_FROM_JOINS = """
    FROM fact_gasto fg
    JOIN (
        SELECT DISTINCT ubigeo,
               TRIM(departamento) AS departamento,
               TRIM(provincia)    AS provincia,
               TRIM(distrito)     AS distrito
        FROM dim_geografica
        QUALIFY ROW_NUMBER() OVER (PARTITION BY ubigeo ORDER BY LENGTH(departamento)) = 1
    ) g ON fg.ubigeo = g.ubigeo
    JOIN dim_tiempo_presupuestal tp ON fg.tiempo_id = tp.tiempo_id
    JOIN dim_entidad e              ON fg.entidad_id = e.entidad_id
    JOIN dim_presupuesto p          ON fg.presupuesto_id = p.presupuesto_id
    JOIN dim_programa_funcional pf  ON fg.programa_id = pf.programa_id
"""


def _q(vals):
    return ", ".join(f"'{v}'" for v in vals)


def _where(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    clauses = []
    if anios:
        clauses.append(f"tp.anio IN ({', '.join(str(a) for a in anios)})")
    if niveles:
        clauses.append(f"e.nivel_gobierno IN ({_q(niveles)})")
    if deptos:
        clauses.append(f"g.departamento IN ({_q(deptos)})")
    if funciones:
        clauses.append(f"pf.funcion_nombre IN ({_q(funciones)})")
    if programas:
        clauses.append(f"pf.programa_ppto_nombre IN ({_q(programas)})")
    return ("WHERE " + " AND ".join(clauses)) if clauses else ""


def opciones_gasto():
    con = get_con()
    anios = [r[0] for r in con.execute(f"""
        SELECT DISTINCT tp.anio {_FROM_JOINS}
        WHERE tp.anio IS NOT NULL ORDER BY 1
    """).fetchall()]
    niveles = [r[0] for r in con.execute(f"""
        SELECT DISTINCT e.nivel_gobierno {_FROM_JOINS}
        WHERE e.nivel_gobierno IS NOT NULL ORDER BY 1
    """).fetchall()]
    deptos = [r[0] for r in con.execute(f"""
        SELECT DISTINCT g.departamento {_FROM_JOINS}
        WHERE g.departamento IS NOT NULL ORDER BY 1
    """).fetchall()]
    funcs = [r[0] for r in con.execute(f"""
        SELECT DISTINCT pf.funcion_nombre {_FROM_JOINS}
        WHERE pf.funcion_nombre IS NOT NULL ORDER BY 1
    """).fetchall()]
    progs = [r[0] for r in con.execute(f"""
        SELECT DISTINCT pf.programa_ppto_nombre {_FROM_JOINS}
        WHERE pf.programa_ppto_nombre IS NOT NULL ORDER BY 1
    """).fetchall()]
    con.close()
    return anios, niveles, deptos, funcs, progs


def kpi_gasto(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    row = con.execute(f"""
        SELECT
            ROUND(SUM(fg.monto_pim)       / 1e9, 2),
            ROUND(SUM(fg.monto_devengado) / 1e9, 2),
            ROUND(SUM(fg.monto_devengado) / NULLIF(SUM(fg.monto_pim), 0) * 100, 1)
        {_FROM_JOINS} {where}
    """).fetchone()
    con.close()
    return {"pim": row[0] or 0, "devengado": row[1] or 0, "tasa": row[2] or 0}


def evolucion_anual(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT tp.anio AS anio,
               ROUND(SUM(fg.monto_pim)       / 1e9, 2) AS pim,
               ROUND(SUM(fg.monto_devengado) / 1e9, 2) AS devengado
        {_FROM_JOINS} {where}
        GROUP BY tp.anio ORDER BY tp.anio
    """).df()
    con.close()
    return df


def top_deptos(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT g.departamento AS departamento,
               ROUND(SUM(fg.monto_pim)       / 1e9, 3) AS pim,
               ROUND(SUM(fg.monto_devengado) / 1e9, 3) AS devengado,
               ROUND(SUM(fg.monto_devengado) / NULLIF(SUM(fg.monto_pim), 0) * 100, 1) AS tasa_ejec
        {_FROM_JOINS} {where}
        GROUP BY g.departamento
        ORDER BY devengado DESC
        LIMIT 15
    """).df()
    con.close()
    return df


def gasto_por_funcion(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT pf.funcion_nombre AS funcion,
               ROUND(SUM(fg.monto_devengado) / 1e9, 2) AS devengado
        {_FROM_JOINS} {where}
        GROUP BY pf.funcion_nombre
        ORDER BY devengado DESC
        LIMIT 12
    """).df()
    con.close()
    return df


def gasto_por_fuente(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT p.fuente_financiamiento AS fuente_financiamiento,
               ROUND(SUM(fg.monto_devengado) / 1e9, 2) AS devengado
        {_FROM_JOINS} {where}
        GROUP BY p.fuente_financiamiento
        ORDER BY devengado DESC
    """).df()
    con.close()
    return df


def gasto_por_nivel(anios=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, None, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT e.nivel_gobierno AS nivel_gobierno,
               ROUND(SUM(fg.monto_pim)       / 1e9, 2) AS pim,
               ROUND(SUM(fg.monto_devengado) / 1e9, 2) AS devengado
        {_FROM_JOINS} {where}
        GROUP BY e.nivel_gobierno
        ORDER BY devengado DESC
    """).df()
    con.close()
    return df


def heatmap_mensual(anios=None, niveles=None, deptos=None, funciones=None, programas=None):
    where = _where(anios, niveles, deptos, funciones, programas)
    con = get_con()
    df = con.execute(f"""
        SELECT tp.anio AS anio, tp.mes AS mes,
               ROUND(SUM(fg.monto_devengado) / 1e6, 1) AS devengado_mill
        {_FROM_JOINS} {where}
        GROUP BY tp.anio, tp.mes
        ORDER BY tp.anio, tp.mes
    """).df()
    con.close()
    return df
