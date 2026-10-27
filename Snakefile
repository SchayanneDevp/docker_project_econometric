
RAW = "01_datos/raw/datal_2017_2026.csv"
PROCESSED = "01_datos/processed/serie_limpia_2017_2026.csv"

GRAFICAS = [
    "03_resultados/graficas/fig1_serie.png",
    "03_resultados/graficas/fig2_despachos.png",
    "03_resultados/graficas/fig3_dispersion.png",
    "03_resultados/graficas/fig4_fac_facp.png",
    "03_resultados/graficas/fig5_residuales.png",
    "03_resultados/graficas/fig6_pronostico.png",
    "03_resultados/graficas/fig7_fac_facp_estacional.png",
    "03_resultados/graficas/fig8_residuos_panel.png",
    "03_resultados/graficas/fig9_raices.png",
    "03_resultados/graficas/fig10_backtest.png",
    "03_resultados/graficas/fig11_estacionalidad.png",
]

TABLAS = [
    "03_resultados/tablas/tabla1_coeficientes.png",
    "03_resultados/tablas/tabla2_pruebas.png",
    "03_resultados/tablas/tabla3_adf_kpss.png",
    "03_resultados/tablas/tabla4_candidatos.png",
]

INFORME = "04_informe/informe.html"


rule all:
    input:
        INFORME


rule preparar_datos:
    input:
        RAW,
        "01_datos/preparar_datos.py"
    output:
        PROCESSED
    shell:
        "python 01_datos/preparar_datos.py"


rule modelo:
    input:
        PROCESSED,
        "02_codigo/02_modelo_final.py"
    output:
        GRAFICAS,
        TABLAS,
        "04_informe/datos.js"
    shell:
        "python 02_codigo/02_modelo_final.py"


rule informe:
    input:
        "04_informe/informe.qmd",
        GRAFICAS,
        TABLAS,
        "04_informe/datos.js"
    output:
        INFORME
    shell:
        "quarto render 04_informe/informe.qmd --to html"
