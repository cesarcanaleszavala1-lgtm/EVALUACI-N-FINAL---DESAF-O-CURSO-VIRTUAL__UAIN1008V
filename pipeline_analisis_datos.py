# -*- coding: utf-8 -*-
"""
UAIN1008V - Análisis de Datos | Optimización de la Cadena de Suministro
Pipeline reproducible: generación -> diagnóstico -> limpieza -> EDA -> KPIs.
Ejecución: python pipeline_analisis_datos.py   (crea ./fig y los CSV/JSON de salida)
Dependencias: Python 3.10+, pandas, numpy, scipy, matplotlib, seaborn
"""
# %% [1] Librerías y parámetros
import json, os, unicodedata, calendar
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

SEED = 2026
rng = np.random.default_rng(SEED)
os.makedirs("fig", exist_ok=True)
R = {}                       # resultados que consume el informe y el panel
MESES = pd.period_range("2025-11", "2026-10", freq="M")
PAISES = ["Perú", "Chile", "Ecuador", "Bolivia"]
CANALES = ["Tradicional", "Moderno", "Mayorista", "E-commerce"]
CATEGORIAS = ["Alimentos", "Cuidado del hogar", "Cuidado personal"]
# Diseño muestral: 5 series (país-canal-categoría) x 12 meses = 60 registros únicos
SERIES = [("Perú", "Tradicional", "Alimentos"), ("Perú", "E-commerce", "Cuidado personal"),
          ("Chile", "Moderno", "Cuidado del hogar"), ("Ecuador", "Mayorista", "Alimentos"),
          ("Bolivia", "Tradicional", "Cuidado personal")]
FILAS_MES = len(SERIES)                                         # 5 registros por mes

# %% [2] Generación del conjunto (el enunciado no adjunta el archivo de ventas)
def generar_datos():
    """Ventas mensuales de 5 series país-canal-categoría (60 registros, 20 variables)."""
    w_pais   = {"Perú": 1.00, "Chile": 0.38, "Ecuador": 0.25, "Bolivia": 0.20}
    p_pais   = {"Perú": 1.00, "Chile": 1.10, "Ecuador": 0.98, "Bolivia": 0.95}
    k_canal  = {"Tradicional": 1.00, "Moderno": 0.30, "Mayorista": 0.20, "E-commerce": 0.08}
    p_canal  = {"Tradicional": 1.00, "Moderno": 1.03, "Mayorista": 0.88, "E-commerce": 1.08}
    d_canal  = {"Tradicional": 4.0, "Moderno": 8.0, "Mayorista": 10.0, "E-commerce": 12.0}
    u_cat    = {"Alimentos": 9000, "Cuidado del hogar": 5000, "Cuidado personal": 4200}
    pr_cat   = {"Alimentos": 8.5, "Cuidado del hogar": 13.0, "Cuidado personal": 16.5}
    cr_cat   = {"Alimentos": 0.68, "Cuidado del hogar": 0.66, "Cuidado personal": 0.62}
    u_serie  = {("Perú", "Tradicional"): 9000, ("Perú", "E-commerce"): 765, ("Chile", "Moderno"): 1400,
                ("Ecuador", "Mayorista"): 1800, ("Bolivia", "Tradicional"): 1080}   # unidades base/mes (calibradas: tradicional ≈ 68 % del valor)
    estac    = [1.05, 1.38, 0.92, 0.90, 1.00, 0.97, 1.03, 1.00, 1.18, 1.02, 0.98, 1.05]
    lead_mu  = {"Perú": 5, "Chile": 6, "Ecuador": 9, "Bolivia": 11}
    cl_pais  = {"Perú": 0.45, "Chile": 0.60, "Ecuador": 0.75, "Bolivia": 0.90}
    cl_canal = {"Tradicional": 1.0, "Moderno": 0.9, "Mayorista": 0.7, "E-commerce": 1.4}
    sig_pron = {"Tradicional": 0.08, "Moderno": 0.10, "Mayorista": 0.12, "E-commerce": 0.20}
    ped_sz   = {"Tradicional": 60, "Moderno": 180, "Mayorista": 450, "E-commerce": 6}
    ot_pais  = {"Perú": 0.93, "Chile": 0.94, "Ecuador": 0.87, "Bolivia": 0.83}
    rep_rng  = {"Perú": (1.00, 1.15), "Chile": (1.00, 1.15), "Ecuador": (0.92, 1.08), "Bolivia": (0.90, 1.05)}
    filas, n = [], 0
    for m, per in enumerate(MESES):
        fecha = per.to_timestamp(how="end").normalize()
        for pa, ca, ct in SERIES:
                if True:
                    n += 1
                    d = float(np.clip(rng.normal(d_canal[ca], 2.5), 0, 25))
                    u = u_serie[(pa, ca)] * estac[m] * (1 + 0.005 * m) \
                        * (1 + 0.004 * d) * rng.lognormal(0, 0.10)
                    u = int(round(u))
                    p = round(pr_cat[ct] * p_canal[ca] * p_pais[pa] * (1 + rng.normal(0, 0.03)), 2)
                    c = round(pr_cat[ct] * cr_cat[ct] * (1 + rng.normal(0, 0.03)), 2)
                    v = round(u * p * (1 - d / 100), 2)
                    pron = int(round(u * np.exp(rng.normal(0.02, sig_pron[ca]))))
                    ini = int(round(u * (0.30 + rng.normal(0, 0.06))))
                    rep = int(round(u * rng.uniform(*rep_rng[pa])))
                    fin = ini + rep - u
                    lead = int(max(2, round(rng.normal(lead_mu[pa], 1.2))))
                    ped = max(5, int(round(u / ped_sz[ca])))
                    pot = ot_pais[pa] - (0.04 if ca == "E-commerce" else 0) - (0.03 if m == 1 else 0)
                    ped_ok = int(rng.binomial(ped, pot))
                    lam = max(0.15, 0.35 * (lead - 3)) * (1.5 if m == 1 else 1.0)
                    dq = int(min(30, rng.poisson(lam)))
                    dev = int(round(u * rng.uniform(0.003, 0.02) * (2.5 if ca == "E-commerce" else 1)))
                    cl = round(cl_pais[pa] * cl_canal[ca] * (1 + rng.normal(0, 0.05)), 2)
                    filas.append(dict(id_registro=f"R{n:04d}", fecha=fecha, pais=pa, canal=ca, categoria=ct,
                        unidades_vendidas=u, precio_unitario=p, descuento_pct=round(d, 1), ventas_netas=v,
                        costo_unitario=c, pronostico_unidades=pron, inventario_inicial=ini,
                        unidades_repuestas=rep, inventario_final=fin, lead_time_dias=lead,
                        pedidos_totales=ped, pedidos_a_tiempo=ped_ok, dias_quiebre=dq,
                        devoluciones_unid=dev, costo_logistico_unit=cl))
    return pd.DataFrame(filas)

def ensuciar(df):
    """Inyecta los problemas descritos en el caso: nulos, duplicados, outliers, formatos y texto."""
    df = df.copy()
    df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d")
    G1 = ["unidades_vendidas", "precio_unitario", "descuento_pct", "ventas_netas"]
    G2 = ["inventario_inicial", "unidades_repuestas", "inventario_final"]
    usado = {"G1": set(), "G2": set(), "otros": set()}
    def grupo(c): return "G1" if c in G1 else ("G2" if c in G2 else "otros")
    def elegir(col, k, excl=()):
        g = grupo(col)
        libres = [i for i in df.index if i not in usado[g] and i not in excl]
        sel = rng.choice(libres, size=k, replace=False)
        usado[g].update(sel); return list(sel)
    # nulos por columna (tasa aproximada 1,2-2,6 %)
    tasa = dict(canal=2, unidades_vendidas=2, precio_unitario=2, descuento_pct=1, ventas_netas=2,
                costo_unitario=2, pronostico_unidades=2, inventario_inicial=1, unidades_repuestas=1,
                inventario_final=2, lead_time_dias=2, pedidos_totales=1, pedidos_a_tiempo=1,
                dias_quiebre=2, devoluciones_unid=2, costo_logistico_unit=2)
    for col, k in tasa.items():
        if col == "canal":
            idx = rng.choice(df.index, size=k, replace=False)
        else:
            idx = elegir(col, k)
        df.loc[idx, col] = np.nan
    ocupadas = lambda g: set(usado[g])
    # valores inválidos (no se solapan con nulos del mismo grupo de identidad)
    ev = []
    for col, k, f in [("unidades_vendidas", 1, lambda s: -s), ("precio_unitario", 1, lambda s: 0.0),
                      ("descuento_pct", 2, lambda s: rng.integers(55, 100)),
                      ("inventario_final", 1, lambda s: -abs(s) - 1)]:
        idx = elegir(col, k)
        df.loc[idx, col] = [f(x) for x in df.loc[idx, col].fillna(100)]
    # errores de digitación x10 en unidades (outliers extremos) en filas sin otros problemas G1/G2
    idx = [i for i in rng.permutation(df.index) if i not in usado["G1"] and i not in usado["G2"]][:3]
    usado["G1"].update(idx); usado["G2"].update(idx)
    df.loc[idx, "unidades_vendidas"] = df.loc[idx, "unidades_vendidas"] * 10
    # outliers de lead time (45-60 días en lugar de 4-6)
    idx = elegir("lead_time_dias", 2)
    df.loc[idx, "lead_time_dias"] = rng.integers(45, 61, size=2)
    # días de quiebre fuera de 0-30
    idx = elegir("dias_quiebre", 2); df.loc[idx, "dias_quiebre"] = [45, -1]
    # pedidos a tiempo > pedidos totales
    idx = elegir("pedidos_a_tiempo", 2)
    df.loc[idx, "pedidos_a_tiempo"] = df.loc[idx, "pedidos_totales"].fillna(50) + rng.integers(3, 15, size=2)
    # formato de fecha DD/MM/AAAA (8 %) y fechas inexistentes (6)
    f = pd.to_datetime(df["fecha"])
    idx = rng.choice(df.index, size=6, replace=False)
    df.loc[idx, "fecha"] = f.loc[idx].dt.strftime("%d/%m/%Y")
    for i in rng.choice(df.index, size=2, replace=False):
        per = f.loc[i]; ult = calendar.monthrange(per.year, per.month)[1]
        df.loc[i, "fecha"] = f"{min(ult + 2, 31):02d}/{per.month:02d}/{per.year}" if ult < 31 else f"31/{per.month - 1 or 12:02d}/{per.year}"
    # texto no estandarizado
    var_p = {"Perú": ["peru", "PERÚ", "Peru ", "perú"], "Chile": ["chile", "CHILE ", "Chile "],
             "Ecuador": ["ecuador", "ECUADOR", "Ecuador "], "Bolivia": ["bolivia", "BOLIVIA", "Bolivia "]}
    var_c = {"Tradicional": ["tradicional", "TRADICIONAL", "Tradicional "], "Moderno": ["moderno", "Moderno "],
             "Mayorista": ["mayorista ", "MAYORISTA", "mayorista"], "E-commerce": ["e-commerce", "Ecommerce", "E-Commerce"]}
    var_k = {"Alimentos": ["alimentos", "ALIMENTOS", "Alimentos "], "Cuidado del hogar": ["cuidado del hogar", "Cuidado Del Hogar", "CUIDADO DEL HOGAR"],
             "Cuidado personal": ["cuidado personal", "Cuidado personal ", "CUIDADO PERSONAL"]}
    for col, var in [("pais", var_p), ("canal", var_c), ("categoria", var_k)]:
        for i in rng.choice(df.index, size=int(0.15 * len(df)), replace=False):
            v = df.at[i, col]
            if isinstance(v, str) and v in var: df.at[i, col] = rng.choice(var[v])
    # duplicados exactos (24), insertados junto al original
    dup_idx = rng.choice(df.index, size=3, replace=False)
    partes, dup_set = [], set(dup_idx)
    for i in df.index:
        partes.append(df.loc[[i]])
        if i in dup_set: partes.append(df.loc[[i]])
    return pd.concat(partes, ignore_index=True)

# %% [3] Carga del conjunto crudo
raw = ensuciar(generar_datos())
raw.to_csv("datos_ventas_raw.csv", index=False, encoding="utf-8-sig")
NUM = ["unidades_vendidas", "precio_unitario", "descuento_pct", "ventas_netas", "costo_unitario",
       "pronostico_unidades", "inventario_inicial", "unidades_repuestas", "inventario_final",
       "lead_time_dias", "pedidos_totales", "pedidos_a_tiempo", "dias_quiebre", "devoluciones_unid",
       "costo_logistico_unit"]
CRIT = ["fecha", "pais", "canal", "unidades_vendidas", "precio_unitario", "ventas_netas"]
R["raw_shape"] = list(raw.shape)

# %% [4] Diagnóstico de calidad (antes de limpiar)
def fecha_valida(s):
    return pd.to_datetime(s, format="%Y-%m-%d", errors="coerce").notna() | \
           pd.to_datetime(s, format="%d/%m/%Y", errors="coerce").notna()

def reglas(df, fechas_ok=None):
    """Violaciones de 8 reglas de consistencia (sobre valores no nulos)."""
    nn = lambda s, cond: int((cond & s.notna()).sum())
    out = {}
    out["R1 unidades_vendidas > 0"] = nn(df.unidades_vendidas, df.unidades_vendidas <= 0)
    out["R2 precio_unitario > 0"] = nn(df.precio_unitario, df.precio_unitario <= 0)
    out["R3 descuento_pct entre 0 y 40"] = nn(df.descuento_pct, (df.descuento_pct < 0) | (df.descuento_pct > 40))
    out["R4 fecha calendario válida"] = int((~fecha_valida(df.fecha.astype(str))).sum()) if fechas_ok is None else fechas_ok
    cat_ok = lambda s, dom: int((~s.isin(dom) & s.notna()).sum())
    out["R5 país/canal/categoría en dominio"] = cat_ok(df.pais, PAISES) + cat_ok(df.canal, CANALES) + cat_ok(df.categoria, CATEGORIAS)
    out["R6 inventario_final >= 0"] = nn(df.inventario_final, df.inventario_final < 0)
    out["R7 dias_quiebre entre 0 y 30"] = nn(df.dias_quiebre, (df.dias_quiebre < 0) | (df.dias_quiebre > 30))
    out["R8 pedidos_a_tiempo <= pedidos_totales"] = int((df.pedidos_a_tiempo > df.pedidos_totales).sum())
    return out

n0 = len(raw)
nulos_col = raw.isna().sum()
R["nulos_por_variable"] = {c: [int(v), round(100 * v / n0, 2)] for c, v in nulos_col.items()}
R["nulos_total"] = [int(nulos_col.sum()), round(100 * nulos_col.sum() / raw.size, 2)]
R["filas_con_nulo"] = [int(raw.isna().any(axis=1).sum()), round(100 * raw.isna().any(axis=1).mean(), 2)]
R["nulos_criticos"] = [int(raw[CRIT].isna().sum().sum()), round(100 * raw[CRIT].isna().sum().sum() / (n0 * len(CRIT)), 2)]
R["duplicados"] = [int(raw.duplicated().sum()), round(100 * raw.duplicated().sum() / n0, 2)]
R["ids_repetidos"] = int(raw.id_registro.duplicated().sum())
R["fechas_ddmm"] = int(raw.fecha.str.contains("/").sum())
R["fechas_invalidas"] = int((~fecha_valida(raw.fecha.astype(str))).sum())
R["unicos_texto_raw"] = {c: int(raw[c].nunique()) for c in ["pais", "canal", "categoria"]}
R["reglas_raw"] = reglas(raw)
R["reglas_raw_total"] = int(sum(R["reglas_raw"].values()))

def outliers(s):
    s = s.dropna(); s = s[s > 0]
    q1, q3 = s.quantile([.25, .75]); iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    z = (s - s.mean()) / s.std()
    mad = (s - s.median()).abs().median()
    mz = 0.6745 * (s - s.median()) / mad
    return dict(n=int(len(s)), iqr_lo=float(lo), iqr_hi=float(hi), iqr=int(((s < lo) | (s > hi)).sum()),
                z=int((z.abs() > 3).sum()), mad=int((mz.abs() > 3.5).sum()), maximo=float(s.max()))
rawd = raw.drop_duplicates()
R["out_unidades"] = outliers(rawd.unidades_vendidas)
R["out_ventas"] = outliers(rawd.ventas_netas)
R["out_lead"] = outliers(rawd.lead_time_dias)
def out_grupo(df0, col):
    """IQR k=1,5 y MAD modificado dentro de cada serie país-canal (n = 12 por serie)."""
    d0 = df0.assign(_p=df0.pais.map(lambda s: unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().strip().lower()),
                    _c=df0.canal.map(lambda s: unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().strip().lower()))
    iq = md = n = 0
    for _, g in d0.groupby(["_p", "_c"]):
        s = g[col].dropna(); s = s[s > 0]; n += len(s)
        if len(s) < 4: continue
        q1, q3 = s.quantile([.25, .75]); i_ = q3 - q1
        iq += int(((s < q1 - 1.5 * i_) | (s > q3 + 1.5 * i_)).sum())
        mad = (s - s.median()).abs().median()
        md += int((0.6745 * (s - s.median()).abs() / mad > 3.5).sum()) if mad > 0 else 0
    return dict(n=n, iqr=iq, mad=md)
R["out_unidades_grupo"] = out_grupo(rawd, "unidades_vendidas")
R["out_ventas_grupo"] = out_grupo(rawd, "ventas_netas")
# integridad antes: ventas = u*p*(1-d) e inventario
def integridad(df):
    v = df.unidades_vendidas * df.precio_unitario * (1 - df.descuento_pct / 100)
    ok1 = (v - df.ventas_netas).abs() <= 0.01 * df.ventas_netas.abs()
    inv = df.inventario_inicial + df.unidades_repuestas - df.unidades_vendidas
    ok2 = (inv - df.inventario_final).abs() <= 1
    c1 = v.notna() & df.ventas_netas.notna(); c2 = inv.notna() & df.inventario_final.notna()
    return dict(ventas_ok=int(ok1[c1].sum()), ventas_n=int(c1.sum()), inv_ok=int(ok2[c2].sum()), inv_n=int(c2.sum()))
R["integridad_raw"] = integridad(rawd)
R["total_ventas_raw"] = float(raw.ventas_netas.sum())
R["media_unid_raw"] = float(raw.unidades_vendidas.mean())

# %% [5] Limpieza y transformación (T1-T7, orden fijo, sin pasos manuales)
df = raw.copy()
# T1. Corrección de tipos y fechas; fecha inexistente -> mes reconstruido con el ID (48 registros por mes)
f1 = pd.to_datetime(df.fecha, format="%Y-%m-%d", errors="coerce")
f2 = pd.to_datetime(df.fecha, format="%d/%m/%Y", errors="coerce")
df["fecha"] = f1.fillna(f2)
inval = df.fecha.isna()
idn = df.id_registro.str[1:].astype(int)
mes_id = ((idn - 1) // FILAS_MES).map(lambda k: MESES[k].to_timestamp(how="end").normalize())
df.loc[inval, "fecha"] = mes_id[inval]
R["t1"] = dict(invalidas_antes=int(inval.sum()), invalidas_despues=int(df.fecha.isna().sum()),
               coincide_id=float(100 * (df.fecha.dt.to_period("M") == mes_id.dt.to_period("M")).mean()))
# T2. Estandarización de texto
def norm(s):
    if pd.isna(s): return s
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().strip().lower()
    return s
mapa = {norm(x): x for x in PAISES + CANALES + CATEGORIAS}
mapa["ecommerce"] = "E-commerce"
for c in ["pais", "canal", "categoria"]:
    df[c] = df[c].map(lambda s: mapa.get(norm(s), np.nan) if pd.notna(s) else s)
R["t2"] = dict(antes=R["unicos_texto_raw"], despues={c: int(df[c].nunique()) for c in ["pais", "canal", "categoria"]})
# T3. Eliminación de duplicados (filas idénticas)
n_a = len(df); df = df.drop_duplicates(subset=["id_registro"]).reset_index(drop=True)
R["t3"] = dict(antes=n_a, despues=len(df), ids_repetidos_despues=int(df.id_registro.duplicated().sum()))
# T4. Valores inválidos -> nulo (regla de dominio)
m1 = df.unidades_vendidas <= 0; m2 = df.precio_unitario <= 0
m3 = (df.descuento_pct < 0) | (df.descuento_pct > 40)
m4 = df.inventario_final < 0; m5 = (df.dias_quiebre < 0) | (df.dias_quiebre > 30)
m6 = df.pedidos_a_tiempo > df.pedidos_totales
R["t4"] = {"unidades": int(m1.sum()), "precio": int(m2.sum()), "descuento": int(m3.sum()),
           "inventario_final": int(m4.sum()), "dias_quiebre": int(m5.sum()), "pedidos_a_tiempo": int(m6.sum())}
df.loc[m1, "unidades_vendidas"] = np.nan; df.loc[m2, "precio_unitario"] = np.nan
df.loc[m3, "descuento_pct"] = np.nan; df.loc[m4, "inventario_final"] = np.nan
df.loc[m5, "dias_quiebre"] = np.nan; df.loc[m6, "pedidos_a_tiempo"] = np.nan
R["t4_total"] = int(sum(R["t4"].values()))
nulos_tras_t4 = int(df.isna().sum().sum())
# T5. Outliers extremos: IQR k=3 por grupo (canal x país). Unidades: corrección por identidad
#     ventas = u*p*(1-d) cuando es posible; si no, winsorización al límite superior. Lead time: winsorización por país.
def limites(col, by, k=3.0):
    g = df.groupby(by)[col]
    q1, q3 = g.transform(lambda s: s.quantile(.25)), g.transform(lambda s: s.quantile(.75))
    return q3 + k * (q3 - q1)
hi_u = limites("unidades_vendidas", ["canal", "pais"])
ext_u = df.unidades_vendidas > hi_u
ident = (df.ventas_netas / (df.precio_unitario * (1 - df.descuento_pct / 100))).round()
corr = ext_u & ident.notna()
R["t5"] = {"unid_extremos": int(ext_u.sum()), "max_antes": float(df.unidades_vendidas.max()),
           "corregidos_identidad": int(corr.sum())}
df.loc[corr, "unidades_vendidas"] = ident[corr]
rest = ext_u & ~corr
df.loc[rest, "unidades_vendidas"] = hi_u[rest].round()
hi_l = limites("lead_time_dias", ["pais"])
ext_l = df.lead_time_dias > hi_l
R["t5"].update(unid_winsor=int(rest.sum()), max_despues=float(df.unidades_vendidas.max()),
               lead_extremos=int(ext_l.sum()), lead_max_antes=float(df.lead_time_dias.max()))
df.loc[ext_l, "lead_time_dias"] = hi_l[ext_l].round()
R["t5"]["lead_max_despues"] = float(df.lead_time_dias.max())
# T6. Imputación: (a) unicidad mes-país-categoría para canal, (b) identidades contables, (c) mediana de razones por grupo
mes = df.fecha.dt.to_period("M")
n_can = int(df.canal.isna().sum())
mapa_c = df.dropna(subset=["canal"]).groupby(["pais", "categoria"]).canal.agg(lambda x: x.mode().iloc[0])
for i in df.index[df.canal.isna()]:
    k = (df.pais[i], df.categoria[i])
    if k in mapa_c.index: df.at[i, "canal"] = mapa_c[k]
R["t6_canal"] = dict(nulos=n_can, resueltos=n_can - int(df.canal.isna().sum()))
nulos_pre = df[NUM].isna().sum().sum()
def ident_g1(df):
    u, p, d, v = df.unidades_vendidas, df.precio_unitario, df.descuento_pct, df.ventas_netas
    m = u.isna() & p.notna() & d.notna() & v.notna(); df.loc[m, "unidades_vendidas"] = (v[m] / (p[m] * (1 - d[m] / 100))).round()
    m = p.isna() & u.notna() & d.notna() & v.notna(); df.loc[m, "precio_unitario"] = (v[m] / (u[m] * (1 - d[m] / 100))).round(2)
    m = d.isna() & u.notna() & p.notna() & v.notna(); df.loc[m, "descuento_pct"] = ((1 - v[m] / (u[m] * p[m])) * 100).clip(0, 40).round(1)
    m = v.isna() & u.notna() & p.notna() & d.notna(); df.loc[m, "ventas_netas"] = (u[m] * p[m] * (1 - d[m] / 100)).round(2)
def ident_g2(df):
    a, r, f, u = df.inventario_inicial, df.unidades_repuestas, df.inventario_final, df.unidades_vendidas
    m = a.isna() & r.notna() & f.notna() & u.notna(); df.loc[m, "inventario_inicial"] = f[m] - r[m] + u[m]
    m = r.isna() & a.notna() & f.notna() & u.notna(); df.loc[m, "unidades_repuestas"] = f[m] - a[m] + u[m]
    m = f.isna() & a.notna() & r.notna() & u.notna(); df.loc[m, "inventario_final"] = a[m] + r[m] - u[m]
ident_g1(df); ident_g2(df)
R["t6_identidad"] = int(nulos_pre - df[NUM].isna().sum().sum())
def imp_ratio(col, base, by):
    ratio = (df[col] / df[base]).groupby([df[b] for b in by]).transform("median")
    m = df[col].isna(); df.loc[m, col] = (df.loc[m, base] * ratio[m]).round()
def imp_med(col, by):
    med = df.groupby(by)[col].transform("median"); m = df[col].isna(); df.loc[m, col] = med[m].round(2)
nulos_med = int(df[NUM].isna().sum().sum())
imp_ratio("pronostico_unidades", "unidades_vendidas", ["canal"])
imp_ratio("pedidos_totales", "unidades_vendidas", ["canal"])
imp_ratio("devoluciones_unid", "unidades_vendidas", ["canal"])
df["pedidos_totales"] = np.maximum(df["pedidos_totales"].clip(lower=1), df["pedidos_a_tiempo"].fillna(0))  # regla R8
imp_ratio("pedidos_a_tiempo", "pedidos_totales", ["pais"])
imp_med("costo_unitario", ["categoria"]); imp_med("lead_time_dias", ["pais"])
imp_med("dias_quiebre", ["pais"]); imp_med("costo_logistico_unit", ["pais", "canal"])
ident_g1(df); ident_g2(df)       # por si alguna identidad quedó resoluble tras imputar
R["t6_mediana"] = int(nulos_med - df[NUM].isna().sum().sum())
R["t6_total"] = R["t6_identidad"] + R["t6_mediana"] + R["t6_canal"]["resueltos"]
R["nulos_pre_imputacion"] = int(nulos_tras_t4)
# T7. Variables derivadas (columnas nuevas) y tipos finales
df["mes"] = df.fecha.dt.strftime("%Y-%m")
df["margen_bruto_pct"] = (df.ventas_netas - df.costo_unitario * df.unidades_vendidas) / df.ventas_netas * 100
df["cobertura_dias"] = df.inventario_final / (df.unidades_vendidas / 30)
df["error_pron_pct"] = (df.pronostico_unidades - df.unidades_vendidas).abs() / df.unidades_vendidas * 100
df["otif_pct"] = df.pedidos_a_tiempo / df.pedidos_totales * 100
for c in ["unidades_vendidas", "inventario_inicial", "unidades_repuestas", "inventario_final", "lead_time_dias",
          "pedidos_totales", "pedidos_a_tiempo", "dias_quiebre", "devoluciones_unid", "pronostico_unidades"]:
    df[c] = df[c].round().astype(int)
DER = ["margen_bruto_pct", "cobertura_dias", "error_pron_pct", "otif_pct"]
NUMF = NUM + DER
df["fecha"] = df.fecha.dt.strftime("%Y-%m-%d")
df.to_csv("datos_ventas_clean.csv", index=False, encoding="utf-8-sig")
R["clean_shape"] = list(df.shape)
R["clean_vars"] = list(df.columns)

# %% [6] Métricas de validación (después)
rl = reglas(df, fechas_ok=int(pd.to_datetime(df.fecha, errors="coerce").isna().sum()))
R["reglas_clean"] = rl
R["nulos_clean"] = int(df.isna().sum().sum())
R["duplicados_clean"] = int(df.duplicated().sum())
R["integridad_clean"] = integridad(df)
R["extremos_clean"] = int((df.unidades_vendidas > hi_u).sum() + (df.lead_time_dias > hi_l).sum())   # mismos límites de T5
R["media_unid_clean"] = float(df.unidades_vendidas.mean())
R["total_ventas_clean"] = float(df.ventas_netas.sum())

# %% [7] Estadística descriptiva
ds = {}
for c in NUMF:
    s = df[c]; q1, q3 = s.quantile([.25, .75])
    ds[c] = dict(media=float(s.mean()), mediana=float(s.median()), sd=float(s.std()), iqr=float(q3 - q1),
                 min=float(s.min()), max=float(s.max()))
R["desc"] = ds
frec = {}
for c in ["canal", "pais", "categoria"]:
    vc = df[c].value_counts(); frec[c] = {k: [int(v), round(100 * v / len(df), 1)] for k, v in vc.items()}
R["frec"] = frec
vc_v = {c: (df.groupby(c).ventas_netas.sum() / df.ventas_netas.sum() * 100).round(1).to_dict() for c in ["canal", "pais", "categoria"]}
R["share_valor"] = vc_v

# %% [8] Relaciones: Spearman, tabla cruzada, Kruskal-Wallis
cols_corr = ["unidades_vendidas", "descuento_pct", "margen_bruto_pct", "lead_time_dias", "dias_quiebre",
             "cobertura_dias", "error_pron_pct", "otif_pct", "costo_logistico_unit"]
cm = df[cols_corr].corr(method="spearman")
R["spearman"] = {f"{a}|{b}": round(float(cm.loc[a, b]), 2) for a in cols_corr for b in cols_corr if a < b}
ic = {c: g[["descuento_pct", "margen_bruto_pct", "unidades_vendidas"]].corr(method="spearman") for c, g in df.groupby("canal")}
R["intra_canal"] = dict(desc_margen=float(np.mean([m.loc["descuento_pct", "margen_bruto_pct"] for m in ic.values()])),
                        desc_unid=float(np.mean([m.loc["descuento_pct", "unidades_vendidas"] for m in ic.values()])))
R["spearman_u_v"] = round(float(df[["unidades_vendidas", "ventas_netas"]].corr(method="spearman").iloc[0, 1]), 2)
R["spearman_p_d_u"] = round(float(df[["precio_unitario", "unidades_vendidas"]].corr(method="spearman").iloc[0, 1]), 2)
ct = pd.crosstab(df.canal, df.pais, values=df.ventas_netas, aggfunc="sum", normalize="columns") * 100
R["cruzada_canal_pais"] = ct.round(1).to_dict()
cc = pd.crosstab(df.canal, df.categoria, values=df.ventas_netas, aggfunc="sum", normalize="index") * 100
R["cruzada_canal_cat"] = cc.round(1).to_dict()
H, pH = stats.kruskal(*[g.ventas_netas.values for _, g in df.groupby("canal")])
R["kruskal_canal"] = dict(H=float(H), p=float(pH), medianas=df.groupby("canal").ventas_netas.median().round(0).to_dict())
H2, pH2 = stats.kruskal(*[g.dias_quiebre.values for _, g in df.groupby("pais")])
R["kruskal_quiebre_pais"] = dict(H=float(H2), p=float(pH2))
# Comparación de grupos (país y canal)
def resumen(by):
    g = df.groupby(by)
    t = pd.DataFrame({
        "ventas": g.ventas_netas.sum(),
        "margen": g.apply(lambda x: (x.ventas_netas.sum() - (x.costo_unitario * x.unidades_vendidas).sum()) / x.ventas_netas.sum() * 100, include_groups=False),
        "wape": g.apply(lambda x: (x.pronostico_unidades - x.unidades_vendidas).abs().sum() / x.unidades_vendidas.sum() * 100, include_groups=False),
        "quiebre": g.dias_quiebre.sum() / (30 * g.size()) * 100,
        "otif": g.pedidos_a_tiempo.sum() / g.pedidos_totales.sum() * 100,
        "cobertura": g.apply(lambda x: x.inventario_final.sum() / (x.unidades_vendidas.sum() / 30), include_groups=False),
        "lead": g.lead_time_dias.mean(), "desc": g.descuento_pct.mean()})
    t["share"] = t.ventas / t.ventas.sum() * 100
    return t.round(2)
R["grupo_pais"] = resumen("pais").to_dict("index"); R["grupo_canal"] = resumen("canal").to_dict("index")
R["grupo_cat"] = resumen("categoria").to_dict("index")
# Estacionalidad
vm = df.groupby("mes").ventas_netas.sum()
R["ventas_mes"] = {k: float(v) for k, v in vm.items()}
R["mom"] = {k: float(v) for k, v in (vm.pct_change() * 100).dropna().items()}
# KPIs globales
tot = df.ventas_netas.sum()
R["kpi"] = dict(
    ventas_total=float(tot), ventas_prom_mes=float(vm.mean()), ventas_oct=float(vm.iloc[-1]), mom_oct=float(vm.pct_change().iloc[-1] * 100),
    margen=float((tot - (df.costo_unitario * df.unidades_vendidas).sum()) / tot * 100),
    wape=float((df.pronostico_unidades - df.unidades_vendidas).abs().sum() / df.unidades_vendidas.sum() * 100),
    sesgo=float((df.pronostico_unidades.sum() / df.unidades_vendidas.sum() - 1) * 100),
    quiebre=float(df.dias_quiebre.sum() / (30 * len(df)) * 100),
    cobertura=float(df.inventario_final.sum() / (df.unidades_vendidas.sum() / 30)),
    otif=float(df.pedidos_a_tiempo.sum() / df.pedidos_totales.sum() * 100),
    lead=float(df.lead_time_dias.mean()),
    peso_trad=float(df[df.canal == "Tradicional"].ventas_netas.sum() / tot * 100),
    dh_nulos_raw=R["nulos_total"][1], dh_dup_raw=R["duplicados"][1])
R["dic_vs_prom"] = float(vm["2025-12"] / vm.mean() * 100 - 100)
R["dic_vs_nov"] = float(vm["2025-12"] / vm["2025-11"] * 100 - 100)
R["corr_lead_quiebre"] = R["spearman"]["dias_quiebre|lead_time_dias"]

# %% [9] Visualizaciones
sns.set_theme(style="whitegrid", font="DejaVu Sans")
plt.rcParams.update({"font.size": 7, "axes.titlesize": 7.6, "axes.labelsize": 6.8, "axes.titleweight": "bold",
                     "xtick.labelsize": 6.2, "ytick.labelsize": 6.2, "legend.fontsize": 6})
AZ = "#2F5597"; NA = "#ED7D31"; GR = "#7F7F7F"
# Figura 1: diagnóstico
fig, ax = plt.subplots(1, 2, figsize=(6.6, 2.3), gridspec_kw={"width_ratios": [1.25, 1]})
nn = pd.Series({k: v[1] for k, v in R["nulos_por_variable"].items() if v[0] > 0}).sort_values()
ax[0].barh(nn.index, nn.values, color=AZ)
for i, v in enumerate(nn.values): ax[0].text(v + 0.05, i, f"{v:.1f}", va="center", fontsize=6)
ax[0].set_title("(a) Nulos por variable (crudo)"); ax[0].set_xlabel("% de filas con dato faltante"); ax[0].tick_params(axis="y", labelsize=6.2)
b = rawd[rawd.unidades_vendidas > 0]
sns.boxplot(data=b, x="canal", y="unidades_vendidas", order=CANALES, ax=ax[1], color="#BDD7EE", fliersize=2, linewidth=.7)
ax[1].set_yscale("log"); ax[1].set_title("(b) Unidades por canal (log)"); ax[1].set_xlabel("Canal")
ax[1].set_ylabel("Unidades por registro (u., log)"); ax[1].tick_params(axis="x", labelsize=6.2)
plt.tight_layout(); plt.savefig("fig/fig1_diagnostico.png", dpi=220); plt.close()
# Figura 2: seis visualizaciones
fig, ax = plt.subplots(2, 3, figsize=(6.9, 4.1))
ax = ax.ravel()
sns.histplot(df.ventas_netas / 1000, bins=14, log_scale=True, color=AZ, ax=ax[0])
ax[0].axvline(df.ventas_netas.mean() / 1000, color=NA, ls="--", lw=1, label=f"media {df.ventas_netas.mean()/1000:,.1f}")
ax[0].axvline(df.ventas_netas.median() / 1000, color="k", ls=":", lw=1, label=f"mediana {df.ventas_netas.median()/1000:,.1f}")
ax[0].legend(fontsize=5.6); ax[0].set_title("(1) Distribución de ventas netas"); ax[0].set_xlabel("Ventas netas por registro (miles S/, log)"); ax[0].set_ylabel("Registros (n)")
vc = df.groupby("categoria").ventas_netas.sum().reindex(CATEGORIAS) / 1e6
ax[1].bar(["Alimentos", "Hogar", "Personal"], vc.values, color=[AZ, NA, GR])
for i, v in enumerate(vc.values): ax[1].text(i, v + 0.05, f"{v:.1f}", ha="center", fontsize=6.2)
ax[1].set_ylim(0, vc.max() * 1.15); ax[1].set_title("(2) Ventas por categoría"); ax[1].set_xlabel("Categoría"); ax[1].set_ylabel("Ventas netas (millones de S/)")
ax[2].plot(range(12), vm.values / 1e6, marker="o", color=AZ, lw=1.4, ms=3)
ax[2].set_xticks(range(0, 12, 2)); ax[2].set_xticklabels([vm.index[i][2:] for i in range(0, 12, 2)], rotation=0)
ax[2].set_title("(3) Ventas mensuales"); ax[2].set_xlabel("Mes (AA-MM)"); ax[2].set_ylabel("Ventas netas (millones de S/)")
sns.boxplot(data=df, x="canal", y="ventas_netas", order=CANALES, ax=ax[3], color="#BDD7EE", fliersize=1.5, linewidth=.7)
ax[3].set_yscale("log"); ax[3].set_xticks(range(4)); ax[3].set_xticklabels(["Trad.", "Mod.", "May.", "E-com."]); ax[3].set_title("(4) Ventas por canal (log)")
ax[3].set_xlabel("Canal"); ax[3].set_ylabel("Ventas netas por registro (S/, log)")
lab = {"unidades_vendidas": "Unid.", "descuento_pct": "Desc.", "margen_bruto_pct": "Margen", "lead_time_dias": "Lead t.",
       "dias_quiebre": "Quiebre", "cobertura_dias": "Cobert.", "error_pron_pct": "Err.pron", "otif_pct": "OTIF", "costo_logistico_unit": "Costo log."}
sns.heatmap(cm.rename(index=lab, columns=lab), annot=True, fmt=".1f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax[4], cbar=False,
            annot_kws={"fontsize": 4.6}, linewidths=.3, xticklabels=True, yticklabels=True)
ax[4].set_title("(5) Correlación de Spearman"); ax[4].tick_params(labelsize=5.0)
for pa, col in zip(PAISES, [AZ, NA, GR, "#70AD47"]):
    s = df[df.pais == pa]; ax[5].scatter(s.lead_time_dias + rng.uniform(-.25, .25, len(s)), s.dias_quiebre, s=6, alpha=.55, color=col, label=pa)
ax[5].legend(fontsize=5.5, loc="upper left"); ax[5].set_title("(6) Lead time vs. quiebre")
ax[5].set_xlabel("Lead time (días)"); ax[5].set_ylabel("Días de quiebre en el mes")
plt.tight_layout(); plt.savefig("fig/fig2_eda.png", dpi=220); plt.close()

# %% [10] Exportar resultados para el informe y el panel
def conv(o):
    if isinstance(o, (np.integer,)): return int(o)
    if isinstance(o, (np.floating,)): return float(o)
    return str(o)
json.dump(R, open("results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=conv)
json.dump(dict(clean=json.loads(df.to_json(orient="records", force_ascii=False)),
               nulos_raw={k: v[1] for k, v in R["nulos_por_variable"].items()},
               dh=dict(nulos=R["nulos_total"][1], dup=R["duplicados"][1], filas_nulo=R["filas_con_nulo"][1])),
          open("dashboard_data.json", "w", encoding="utf-8"), ensure_ascii=False)
print("OK", R["raw_shape"], R["clean_shape"])
