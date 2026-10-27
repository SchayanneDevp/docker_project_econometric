# %% [BLOQUE 0] CONFIGURACIÓN Y RUTAS
# ============================================================================
# Proyecto: Modelado de la Demanda de Pasajeros (2017-2026)
# Metodología: Box-Jenkins (Guerrero, 2003; Enders, 2014)
# ============================================================================
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
from statsmodels.stats.stattools import durbin_watson
from scipy.stats import jarque_bera, shapiro, kurtosis, probplot, norm
from arch import arch_model

warnings.filterwarnings("ignore")

# Estilo académico
plt.rcParams.update({
    "font.family": "serif", "font.size": 10, "axes.labelsize": 10,
    "axes.titlesize": 11, "figure.dpi": 150, "savefig.bbox": "tight"
})


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PROC = (
    BASE_DIR / "01_datos" / "processed"
    / "serie_limpia_2017_2026.csv"
)

POSTER_DIR = BASE_DIR / "04_informe"
IMG_GRAF = BASE_DIR / "03_resultados" / "graficas"
IMG_TABL = BASE_DIR / "03_resultados" / "tablas"

POSTER_DIR.mkdir(parents=True, exist_ok=True)
IMG_GRAF.mkdir(parents=True, exist_ok=True)
IMG_TABL.mkdir(parents=True, exist_ok=True)

print("="*70)
print("SCRIPT MAESTRO: MODELADO ACADÉMICO")
print("="*70)

# %% [BLOQUE 1] CARGA Y PREPARACIÓN DE DATOS
# ============================================================================
# Motivación: Serie de salidas de pasajeros desde Bogotá.
# Es un proxy de la actividad económica y la movilidad.
# ============================================================================
df = pd.read_csv(DATA_PROC, parse_dates=["fecha"], index_col="fecha")
pasajeros = df["pasajeros"]
despachos = df["despachos"]

pasajeros_log = np.log(pasajeros + 1)
despachos_log = np.log(despachos + 1)

# Dummies
dummy_pandemia = pd.Series(0, index=pasajeros.index, name="Pandemia")
dummy_pandemia[(pasajeros.index >= "2020-03-01") & (pasajeros.index <= "2020-12-31")] = 1
dummy_dic2019 = pd.Series(0, index=pasajeros.index, name="Dic2019")
dummy_dic2019[(pasajeros.index >= "2019-12-01") & (pasajeros.index <= "2019-12-31")] = 1
dummy_dic2020 = pd.Series(0, index=pasajeros.index, name="Dic2020")
dummy_dic2020[(pasajeros.index >= "2020-12-01") & (pasajeros.index <= "2020-12-31")] = 1

exog = pd.DataFrame({
    "Pandemia": dummy_pandemia, "Dic2019": dummy_dic2019,
    "Dic2020": dummy_dic2020, "Despachos_Log": despachos_log
})

# %% [BLOQUE 2] GRÁFICAS EXPLORATORIAS
# ============================================================================
# Fig 1: Serie histórica | Fig 2: Despachos | Fig 3: Dispersión
# ============================================================================
plt.figure(figsize=(8, 4))
plt.plot(pasajeros.index, pasajeros.values, color="black", linewidth=1)
plt.title("Serie Histórica de Pasajeros (2017-2026)")
plt.xlabel("Año"); plt.ylabel("Pasajeros")
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig(IMG_GRAF / "fig1_serie.png"); plt.close()

plt.figure(figsize=(8, 4))
plt.plot(despachos.index, despachos.values, color="darkgreen", linewidth=1)
plt.title("Serie Exógena: Despachos de Buses (2017-2026)")
plt.xlabel("Año"); plt.ylabel("Despachos")
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig(IMG_GRAF / "fig2_despachos.png"); plt.close()

plt.figure(figsize=(6, 4))
plt.scatter(despachos, pasajeros, color="purple", alpha=0.6, edgecolors="black")
plt.title("Relación Oferta-Demanda")
plt.xlabel("Despachos (Oferta)"); plt.ylabel("Pasajeros (Demanda)")
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig(IMG_GRAF / "fig3_dispersion.png"); plt.close()

# %% [BLOQUE 3] GRÁFICAS DE IDENTIFICACIÓN (FAC/FACP)
# ============================================================================
# Fig 4: FAC/FACP de la serie diferenciada.
# Fig 7: FAC/FACP estacional (justifica el MA(12)).
# ============================================================================
serie_diff = pasajeros_log.diff().dropna()
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
plot_acf(serie_diff, lags=24, ax=axes[0], alpha=0.05)
axes[0].set_title("FAC (Serie Diferenciada)")
plot_pacf(serie_diff, lags=24, ax=axes[1], alpha=0.05)
axes[1].set_title("FACP (Serie Diferenciada)")
plt.tight_layout(); plt.savefig(IMG_GRAF / "fig4_fac_facp.png"); plt.close()

serie_dd12 = pasajeros_log.diff(12).diff().dropna()
fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
plot_acf(serie_dd12, lags=36, ax=axes[0], alpha=0.05)
axes[0].set_title("FAC — ΔΔ₁₂ ln(y)")
plot_pacf(serie_dd12, lags=36, ax=axes[1], alpha=0.05)
axes[1].set_title("FACP — ΔΔ₁₂ ln(y)")
plt.tight_layout(); plt.savefig(IMG_GRAF / "fig7_fac_facp_estacional.png"); plt.close()

# %% [BLOQUE 4] ESTIMACIÓN DEL MODELO SARIMAX + GARCH
# ============================================================================
# Modelo: SARIMAX(2,1,2)(0,1,1,12) + Log + Despachos + Dummies.
# ============================================================================
modelo = SARIMAX(
    pasajeros_log, exog=exog, order=(2,1,2), seasonal_order=(0,1,1,12),
    trend="n", enforce_stationarity=False, enforce_invertibility=False
)
estimacion = modelo.fit(disp=False)
residuos = estimacion.resid.dropna()

# GARCH(1,1)
residuos_esc = residuos * 100
garch = arch_model(residuos_esc, vol="Garch", p=1, q=1, dist="normal").fit(disp="off")
residuos_est = garch.resid / garch.conditional_volatility

# %% [BLOQUE 5] GRÁFICAS DE VALIDACIÓN Y PRONÓSTICO
# ============================================================================
# Fig 5: Residuales estandarizados.
# Fig 8: Panel de 4 diagnósticos (residuos, ACF, hist, QQ).
# Fig 9: Raíces AR/MA.
# Fig 6: Pronóstico.
# ============================================================================
plt.figure(figsize=(8, 4))
plt.plot(residuos_est.index, residuos_est.values, color="darkred", linewidth=0.8)
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("Residuales Estandarizados (Post-GARCH)")
plt.xlabel("Año"); plt.ylabel("Error")
plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig(IMG_GRAF / "fig5_residuales.png"); plt.close()

# Panel de 4 diagnósticos
resid_std = (residuos - residuos.mean()) / residuos.std()
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
axes[0,0].plot(residuos.index, resid_std.values, color="black", linewidth=0.7)
axes[0,0].axhline(0, color="grey", linewidth=0.6)
axes[0,0].set_title("Residuos estandarizados")
plot_acf(residuos, lags=36, ax=axes[0,1], alpha=0.05)
axes[0,1].set_title("ACF de residuos")
axes[1,0].hist(residuos, bins=25, density=True, color="white", edgecolor="black")
_x = np.linspace(residuos.min(), residuos.max(), 200)
axes[1,0].plot(_x, norm.pdf(_x, residuos.mean(), residuos.std()), color="black")
axes[1,0].set_title("Histograma vs normal")
probplot(residuos, dist="norm", plot=axes[1,1])
axes[1,1].set_title("QQ-plot")
plt.tight_layout(); plt.savefig(IMG_GRAF / "fig8_residuos_panel.png"); plt.close()

# Raíces AR/MA
try:
    _ar, _ma = estimacion.arroots, estimacion.maroots
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.add_patch(plt.Circle((0,0), 1, fill=False, edgecolor="black"))
    ax.scatter(_ar.real, _ar.imag, marker="x", color="black", s=50, label="Raíces AR")
    ax.scatter(_ma.real, _ma.imag, marker="o", facecolors="none", edgecolors="black", s=50, label="Raíces MA")
    ax.axhline(0, color="grey"); ax.axvline(0, color="grey")
    ax.set_xlim(-2,2); ax.set_ylim(-2,2); ax.set_aspect("equal")
    ax.set_title("Figura 9. Raíces AR y MA")
    ax.legend(frameon=False)
    plt.tight_layout(); plt.savefig(IMG_GRAF / "fig9_raices.png"); plt.close()
except: pass

# Pronóstico
ultimo_despacho_log = despachos_log.iloc[-1]
fechas_futuras = pd.date_range(start=pasajeros.index[-1] + pd.DateOffset(months=1), periods=10, freq="MS")
exog_futuro = pd.DataFrame({
    "Pandemia": [0]*10, "Dic2019": [0]*10, "Dic2020": [0]*10,
    "Despachos_Log": [ultimo_despacho_log]*10
}, index=fechas_futuras)
pron = estimacion.get_forecast(steps=10, exog=exog_futuro)
pron_nivel = np.exp(pron.predicted_mean) - 1
intervalos = np.exp(pron.conf_int()) - 1
intervalos[intervalos < 0] = 0

plt.figure(figsize=(8, 4))
plt.plot(pasajeros.index[-36:], pasajeros.values[-36:], label="Histórico", color="black")
plt.plot(pron_nivel.index, pron_nivel.values, label="Pronóstico", color="darkorange", linewidth=2)
plt.fill_between(pron_nivel.index, intervalos.iloc[:,0], intervalos.iloc[:,1], color="orange", alpha=0.3, label="IC 95%")
plt.title("Pronóstico de Pasajeros (10 Meses)")
plt.xlabel("Año"); plt.ylabel("Pasajeros")
plt.legend(); plt.grid(True, linestyle="--", alpha=0.6)
plt.savefig(IMG_GRAF / "fig6_pronostico.png"); plt.close()

# %% [BLOQUE 6] GRÁFICAS ADICIONALES (BACK-TEST Y ESTACIONALIDAD)
# ============================================================================
# Fig 10: Back-test 12 meses con MAPE.
# Fig 11: Perfil estacional medio por mes (sin COVID).
# ============================================================================
# Back-test
try:
    n_test = 12
    train, test = pasajeros_log.iloc[:-n_test], pasajeros_log.iloc[-n_test:]
    exog_train, exog_test = exog.iloc[:-n_test], exog.iloc[-n_test:]
    m = SARIMAX(train, exog=exog_train, order=(2,1,2), seasonal_order=(0,1,1,12), trend="n")
    r = m.fit(disp=False)
    p = r.get_forecast(steps=n_test, exog=exog_test)
    pred = np.exp(p.predicted_mean) - 1
    ic = np.exp(p.conf_int()) - 1
    ic[ic < 0] = 0
    real = np.exp(test) - 1
    mape = np.mean(np.abs((real.values - pred.values) / real.values)) * 100
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(real.index, real.values, "k-", marker="o", markersize=3, label="Observado")
    ax.plot(pred.index, pred.values, "k--", label="Predicho")
    ax.fill_between(pred.index, ic.iloc[:,0], ic.iloc[:,1], color="grey", alpha=0.3, label="IC 95%")
    ax.set_title(f"Figura 10. Back-test 12 meses (MAPE = {mape:.2f}%)")
    ax.legend(frameon=False); plt.tight_layout()
    plt.savefig(IMG_GRAF / "fig10_backtest.png"); plt.close()
except: pass

# Perfil estacional
mask_pre = (pasajeros.index < "2020-03-01") | (pasajeros.index > "2021-06-30")
pas_est = pasajeros[mask_pre]
perfil = pas_est.groupby(pas_est.index.month).mean()
meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.bar(meses, perfil.values, color="white", edgecolor="black")
ax.set_title("Figura 11. Perfil estacional medio por mes (sin COVID)")
ax.set_ylabel("Pasajeros promedio"); ax.set_xlabel("Mes")
plt.tight_layout(); plt.savefig(IMG_GRAF / "fig11_estacionalidad.png"); plt.close()

# %% [BLOQUE 7] TABLAS (SE GUARDAN EN IMG_TABL)
# ============================================================================
# Tabla 1: Coeficientes | Tabla 2: Pruebas | Tabla 3: ADF/KPSS
# Tabla 4: Comparación de candidatos
# ============================================================================
# Tabla 1: Coeficientes
params = estimacion.params; pvalues = estimacion.pvalues
tabla_coef = pd.DataFrame({"Variable": params.index, "Coeficiente": params.values, "p-valor": pvalues.values})
fig, ax = plt.subplots(figsize=(6, 3)); ax.axis("off")
tb1 = ax.table(cellText=tabla_coef.round(4).values, colLabels=tabla_coef.columns, loc="center", cellLoc="center")
tb1.auto_set_font_size(False); tb1.set_fontsize(10); tb1.scale(1.2, 1.2)
plt.title("Tabla 1. Coeficientes del Modelo SARIMAX")
plt.savefig(IMG_TABL / "tabla1_coeficientes.png"); plt.close()

# Tabla 2: Pruebas
lb = acorr_ljungbox(residuos_est, lags=[6, 12], return_df=True)
p_arch = het_arch(residuos_est, nlags=12)[1]
p_jb = jarque_bera(residuos_est).pvalue
p_sw = shapiro(residuos_est).pvalue
dw = durbin_watson(residuos_est)
kurt = kurtosis(residuos_est, fisher=True) + 3

tabla_pruebas = pd.DataFrame({
    "Prueba": ["Ljung-Box (6)", "Ljung-Box (12)", "ARCH", "Jarque-Bera", "Shapiro-Wilk", "Durbin-Watson", "Curtosis"],
    "Valor": [f"{lb['lb_pvalue'].iloc[0]:.4f}", f"{lb['lb_pvalue'].iloc[1]:.4f}", f"{p_arch:.4f}", f"{p_jb:.4f}", f"{p_sw:.4f}", f"{dw:.4f}", f"{kurt:.4f}"],
    "Conclusión": ["Pasa" if lb['lb_pvalue'].iloc[0] > 0.05 else "Falla", "Pasa" if lb['lb_pvalue'].iloc[1] > 0.05 else "Falla (leve)", "Pasa" if p_arch > 0.05 else "Falla", "Pasa" if p_jb > 0.05 else "Falla", "Pasa" if p_sw > 0.05 else "Falla", "Pasa" if 1.5 < dw < 2.5 else "Falla", "Aceptable" if kurt < 4.5 else "Alta"]
})
fig, ax = plt.subplots(figsize=(6, 3)); ax.axis("off")
tb2 = ax.table(cellText=tabla_pruebas.values, colLabels=tabla_pruebas.columns, loc="center", cellLoc="center")
tb2.auto_set_font_size(False); tb2.set_fontsize(10); tb2.scale(1.2, 1.2)
plt.title("Tabla 2. Pruebas de Validación")
plt.savefig(IMG_TABL / "tabla2_pruebas.png"); plt.close()

# Tabla 3: ADF/KPSS
def _pruebas_raiz(serie, nombre):
    serie = serie.dropna()
    adf_p = adfuller(serie, autolag="AIC")[1]
    kpss_p = kpss(serie, regression="c", nlags="auto")[1]
    return {"Serie": nombre, "ADF (p)": f"{adf_p:.4f}", "ADF decisión": "Estacionaria" if adf_p < 0.05 else "No estacionaria", "KPSS (p)": f"{kpss_p:.4f}", "KPSS decisión": "Estacionaria" if kpss_p > 0.05 else "No estacionaria"}

serie_d = pasajeros_log.diff().dropna()
serie_dd12 = pasajeros_log.diff(12).diff().dropna()
sub = pasajeros_log["2021-07-01":]
sub_d = sub.diff().dropna()
sub_dd12 = sub.diff(12).diff().dropna()

tabla_adf = pd.DataFrame([
    _pruebas_raiz(pasajeros_log, "ln(y) — completa"),
    _pruebas_raiz(serie_dd12, "ΔΔ₁₂ ln(y) — completa"),
    _pruebas_raiz(sub, "ln(y) — post-2021"),
    _pruebas_raiz(sub_d, "Δ ln(y) — post-2021"),
    _pruebas_raiz(sub_dd12, "ΔΔ₁₂ ln(y) — post-2021"),
])
fig, ax = plt.subplots(figsize=(9, 0.42 * len(tabla_adf) + 1.8)); ax.axis("off")
tb3 = ax.table(cellText=tabla_adf.values, colLabels=tabla_adf.columns, loc="center", cellLoc="center")
tb3.auto_set_font_size(False); tb3.set_fontsize(8.5); tb3.scale(1, 1.5)
plt.title("Tabla 3. Pruebas de raíz unitaria (ADF y KPSS)")
plt.savefig(IMG_TABL / "tabla3_adf_kpss.png"); plt.close()

# Tabla 4: Comparación de modelos candidatos
candidatos = [((2,1,2), (0,1,1,12)), ((2,1,1), (0,1,1,12)), ((2,1,0), (0,1,1,12)), ((1,1,1), (0,1,1,12)), ((0,1,1), (0,1,1,12)), ((3,1,2), (0,1,1,12)), ((2,1,2), (1,1,1,12))]
filas = []
for _o, _so in candidatos:
    try:
        _m = SARIMAX(pasajeros_log, exog=exog, order=_o, seasonal_order=_so, trend="n", enforce_stationarity=False, enforce_invertibility=False)
        _r = _m.fit(disp=False)
        filas.append({"Modelo": f"({_o[0]},{_o[1]},{_o[2]})({_so[0]},{_so[1]},{_so[2]},{_so[3]})", "AIC": f"{_r.aic:.2f}", "BIC": f"{_r.bic:.2f}", "LogLik": f"{_r.llf:.2f}"})
    except:
        filas.append({"Modelo": f"({_o[0]},{_o[1]},{_o[2]})({_so[0]},{_so[1]},{_so[2]},{_so[3]})", "AIC": "—", "BIC": "—", "LogLik": "—"})
tabla_cand = pd.DataFrame(filas).sort_values("AIC").reset_index(drop=True)
fig, ax = plt.subplots(figsize=(8, 0.45 * len(tabla_cand) + 1.4)); ax.axis("off")
tb4 = ax.table(cellText=tabla_cand.values, colLabels=tabla_cand.columns, loc="center", cellLoc="center")
tb4.auto_set_font_size(False); tb4.set_fontsize(8.5); tb4.scale(1, 1.4)
plt.title("Tabla 4. Comparación de modelos (menor AIC es mejor)")
plt.savefig(IMG_TABL / "tabla4_candidatos.png"); plt.close()

# %% [BLOQUE 8] EXPORTACIÓN DE DATOS (datos.js)
# ============================================================================
# Datos dinámicos para el HTML (por si se necesitan).
# ============================================================================
datos_dinamicos = {
    "aic": f"{estimacion.aic:.2f}",
    "conclusion": f"El modelo SARIMAX(2,1,2)(0,1,1,12) alcanzó un AIC de {estimacion.aic:.2f}."
}
with open(POSTER_DIR / "datos.js", "w", encoding="utf-8") as f:
    f.write(f"const datosDinamicos = {json.dumps(datos_dinamicos, ensure_ascii=False)};")

print("\n Script finalizado. Revisa las carpetas:")
print(f"  - Gráficas: {IMG_GRAF}")
print(f"  - Tablas:   {IMG_TABL}")