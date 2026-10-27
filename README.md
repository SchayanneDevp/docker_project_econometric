\# Análisis econométrico de la demanda mensual de pasajeros



\## 1. Descripción del proyecto



Este proyecto implementa un flujo reproducible de análisis econométrico de la demanda mensual de pasajeros para el periodo 2017–2026, utilizando Python, Docker, Snakemake y Quarto.



El objetivo es procesar los datos, realizar análisis estadísticos y econométricos, generar gráficos y tablas, y construir un informe HTML con los principales resultados.



El entorno de ejecución está definido mediante Docker para facilitar la reproducción del análisis en diferentes computadores sin necesidad de instalar manualmente todas las dependencias de Python.



\## 2. Tecnologías utilizadas



\- \*\*Python:\*\* procesamiento de datos y análisis econométrico.

\- \*\*Pandas y NumPy:\*\* manipulación y cálculo de datos.

\- \*\*Matplotlib y Seaborn:\*\* visualización de resultados.

\- \*\*Statsmodels y SciPy:\*\* herramientas estadísticas y econométricas.

\- \*\*ARCH:\*\* herramientas para modelación de series temporales.

\- \*\*Snakemake:\*\* automatización y organización del flujo de trabajo.

\- \*\*Quarto:\*\* generación del informe HTML.

\- \*\*Docker:\*\* construcción de un entorno reproducible.

\- \*\*Git y GitHub:\*\* control de versiones y distribución del código.



\## 3. Estructura del proyecto



```text

docker\_project\_econometric/

├── 01\_datos/

│   ├── raw/

│   │   └── datal\_2017\_2026.csv

│   ├── processed/

│   │   └── serie\_limpia\_2017\_2026.csv

│   └── preparar\_datos.py

├── 02\_codigo/

│   └── 02\_modelo\_final.py

├── 03\_resultados/

│   ├── graficas/

│   └── tablas/

├── 04\_informe/

│   ├── datos.js

│   ├── informe.qmd

│   └── informe.html

├── Dockerfile

├── environment.yml

├── Snakefile

├── .gitignore

└── README.md

```



Los resultados generados pueden incluir gráficos, tablas estadísticas, diagnósticos de modelos y pronósticos, según las reglas definidas en el flujo de trabajo.



\## 4. Requisitos previos



Antes de ejecutar el proyecto, se necesita:



1\. Un computador con Windows, macOS o Linux.

2\. Git instalado.

3\. Docker Desktop en Windows o macOS, o Docker Engine en Linux.

4\. Conexión a Internet para descargar el código y construir la imagen de Docker.



En Windows, Docker Desktop debe estar instalado y ejecutándose antes de continuar.



\### Verificar las instalaciones



Abre una terminal y ejecuta:



```powershell

git --version

docker --version

docker info

```



Los dos primeros comandos deben mostrar las versiones instaladas. El comando `docker info` permite comprobar si el motor de Docker está disponible.



\## 5. Instalar Docker



\### Windows



1\. Visita la página oficial: https://www.docker.com/products/docker-desktop/

2\. Descarga Docker Desktop para Windows.

3\. Sigue el instalador y las instrucciones oficiales.

4\. Reinicia el equipo si el instalador lo solicita.

5\. Abre Docker Desktop y espera a que el motor esté funcionando.

6\. Verifica la instalación ejecutando `docker info` en PowerShell.



Consulta los requisitos del sistema y las instrucciones oficiales de instalación antes de instalarlo.



\### macOS



Descarga Docker Desktop para Mac desde la página oficial y sigue las instrucciones correspondientes a tu equipo.



\### Linux



Instala Docker Engine siguiendo la documentación oficial de Docker para tu distribución.



\## 6. Descargar el proyecto desde GitHub



Abre PowerShell, Terminal o una consola compatible y dirígete a la carpeta donde quieras guardar el proyecto.



Ejecuta:



```powershell

git clone https://github.com/SchayanneDevp/docker\_project\_econometric.git

cd docker\_project\_econometric

```



El primer comando descarga el repositorio y el segundo entra en la carpeta del proyecto.



\## 7. Construir la imagen de Docker



Desde la carpeta raíz del proyecto, ejecuta:



```powershell

docker build -t analisis-pasajeros .

```



Este comando construye la imagen a partir del `Dockerfile` y prepara las dependencias declaradas en `environment.yml`.



La primera construcción puede tardar varios minutos porque Docker debe descargar la imagen base e instalar los paquetes necesarios.



No es necesario descargar ni importar un archivo `.tar` de la imagen Docker: la imagen se construye localmente a partir del código del repositorio.



\## 8. Ejecutar el análisis



Una vez construida la imagen, ejecuta el siguiente comando.



\### Windows PowerShell



```powershell

docker run --rm -v "${PWD}:/proyecto" analisis-pasajeros

```



\### macOS o Linux



```bash

docker run --rm -v "$PWD:/proyecto" analisis-pasajeros

```



El comando ejecuta el flujo de trabajo definido en el `Snakefile`.



\- `docker run` ejecuta un contenedor a partir de la imagen.

\- `--rm` elimina el contenedor al terminar, pero no borra los archivos del proyecto.

\- `-v` permite que el contenedor acceda a la carpeta del proyecto y que los resultados generados queden disponibles en el computador.

\- `analisis-pasajeros` es el nombre de la imagen construida.



El flujo de trabajo prepara los datos, ejecuta las reglas de análisis y genera los resultados definidos por Snakemake.



Espera a que el proceso termine y revisa la terminal para comprobar si hubo errores.



\## 9. Consultar el informe HTML



Al finalizar correctamente el flujo de trabajo, busca el informe en:



```text

04\_informe/informe.html

```



Abre el archivo con un navegador web, por ejemplo, Chrome, Edge o Firefox.



El informe presenta los resultados que se hayan generado a partir del código y los datos disponibles.



\## 10. Volver a ejecutar el proyecto



Si necesitas ejecutar nuevamente el análisis, desde la carpeta raíz puedes usar:



```powershell

docker run --rm -v "${PWD}:/proyecto" analisis-pasajeros

```



Si cambias el `Dockerfile` o las dependencias de `environment.yml`, reconstruye la imagen:



```powershell

docker build -t analisis-pasajeros .

```



Si cambias el código fuente, los datos o las reglas de Snakemake, vuelve a ejecutar el flujo de trabajo y verifica los resultados.



\## 11. Archivos y resultados



\- `01\_datos/raw/`: datos de entrada.

\- `01\_datos/processed/`: datos procesados.

\- `02\_codigo/`: código principal del análisis econométrico.

\- `03\_resultados/graficas/`: gráficos generados.

\- `03\_resultados/tablas/`: tablas generadas.

\- `04\_informe/informe.qmd`: documento fuente del informe.

\- `04\_informe/informe.html`: informe generado.

\- `Snakefile`: reglas que organizan la ejecución del flujo de trabajo.

\- `Dockerfile`: instrucciones para construir la imagen de Docker.

\- `environment.yml`: definición del entorno y sus dependencias.



\## 12. Solución de problemas



\### Docker no está iniciado



Abre Docker Desktop y espera hasta que indique que está funcionando. Después vuelve a ejecutar el comando.



\### No se encuentra el comando `docker`



Comprueba que Docker esté instalado y que la terminal pueda acceder a él. Si acabas de instalarlo, reinicia la terminal.



\### La construcción de la imagen falla



Revisa la conexión a Internet y el mensaje de error de `docker build`. La construcción puede fallar si no se pueden descargar la imagen base o las dependencias.



\### El informe HTML no aparece o está desactualizado



Comprueba que el flujo de trabajo haya terminado sin errores y revisa la salida de Snakemake en la terminal. Verifica también la existencia de `04\_informe/informe.html`.



\### Necesito reconstruir la imagen



Ejecuta nuevamente:



```powershell

docker build -t analisis-pasajeros .

```



\## 13. Reproducibilidad



Docker permite definir un entorno de ejecución común, mientras que Snakemake organiza las tareas y sus dependencias.



La reproducibilidad de los resultados también depende de la disponibilidad de los datos originales, las versiones de las dependencias y el código utilizado.



\## 14. Repositorio



Código fuente disponible en GitHub:



https://github.com/SchayanneDevp/docker\_project\_econometric



