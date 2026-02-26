# 🏦 Modelo Predictivo de Riesgo Crediticio (MLOps)

## OBJETIVO:
Implementar un motor predictivo de riesgo crediticio para reducir el DEFAUL y monimizar LTV mediante
la identificacion anticipada de perfiles de usuario. Se diseño un pepiline robusto capaz de transformar datos 
inconsistentes en señales confiables, garantizando la puesta de produccion inmediata mediante el cumplimiento 
estricto de la arquitecctura exigida por los procesos de CI/CD en Jenkins

## TECNOLOGIA/STACK 

- Lenguajes y Análisis: Python, Pandas, Numpy, Matplotlib, Seaborn.
- Machine Learning: Scikit-Learn, XGBoost, Joblib.
- MLOps & Despliegue: FastAPI (API), Docker & Docker-Compose, Streamlit (Dashboard).
- Monitoreo: Evidently AI, Scipy (KS-test), PSI (Population Stability Index).

## ESTRUCTURAS DE CARPETAS:

### src/: Directorio raíz del código fuente modularizado.
- Carga_datos.py: Script para la ingesta y lectura de fuentes de datos.
- Comprension_EDA.ipynb: Notebook de experimentación y diagnóstico estadístico.
- ft_engineerings.py: Módulo de transformación y creación de variables.
- model_training_evaluation.ipynb: Pipeline de entrenamiento y validación de modelos.
- model_deploy.py y model_monitoring.py: Scripts para el servicio de API y control de deriva de datos.
### venv/: Entorno virtual para el aislamiento de dependencias del proyecto.
- Raíz del Proyecto (/): Contiene los archivos de orquestación y despliegue.
- Dockerfile.api y Dockerfile.dashboard: Definiciones para la containerización.
- docker-compose.yml: Orquestador de servicios.
- requirements.txt: Lista de librerías necesarias para el entorno.
- app.py: Punto de entrada para la aplicación/dashboard.

## STORYTELLING DEL PROYECTO : 

# 📈 Avance 1: Diagnóstico y Comprensión de Datos
En esta etapa inicial, el enfoque fue identificar la viabilidad del proyecto dada la baja calidad de la fuente original.

1. Ingesta Técnica de Datos
Se desarrolló un proceso de carga robusto mediante Carga_datos.py para leer el archivo Base_de_datos.xlsx.

Centralizar la carga en un script independiente para asegurar que cualquier cambio en la fuente de datos solo requiera modificar un único punto del pipeline.

2. Análisis Exploratorio (EDA) y Auditoría de Calidad
Se realizó un perfilamiento de datos en Comprension_EDA.ipynb evaluando tipos de datos, nulos y distribuciones.

Hallazgos Críticos:
Se detectaron columnas con nulos masivos: id_punto_venta (100% nulos) e id_solicitud (99.9% nulos).
Se identificó un desbalanceo en la variable objetivo.

Se decidio eliminar las variables con más del 90% de nulos en lugar de imputarlas, ya que la imputación en estos niveles introduciría un sesgo inaceptable en el modelo predictivo.

3. Resultados del Avance 1
Se estableció un set de datos de referencia (data_referencia.csv) para futuras validaciones.
Se determinó que, aunque la base de datos es "imperfecta", las variables financieras clave tienen suficiente señal para proceder con el modelado.

# 🛠 Avance 2: Preprocesamiento e Ingeniería de Variables (Feature Engineering)
El objetivo fue construir un Pipeline de procesamiento robusto que mitigue las inconsistencias detectadas en el Avance 1 y prepare los datos para algoritmos de Machine Learning de alto rendimiento.

1. Construcción del Pipeline de Transformación
Se desarrolló el módulo ft_engineerings.py utilizando ColumnTransformer y Pipeline de Scikit-Learn.

Se separaron las variables en tres grupos: 
- Numéricas
- Categóricas  
- Ordinales
Donde se aplico una estrategia específica para cada una.

Para las variables numéricas, se optó por la imputación por mediana (SimpleImputer), una decisión técnica para evitar que los valores extremos (outliers) de la base de datos original sesgaran el promedio.

Estandarización: Se aplicó StandardScaler para asegurar que todas las variables numéricas estén en la misma escala, optimizando así la convergencia de modelos como SVM o Regresión Logística.

2. Codificación y Consistencia de Datos
Implementación de OneHotEncoder para variables como tipo_laboral y tendencia_ingresos.

Se utilizó el parámetro handle_unknown="ignore" en el Encoder. Permimtiendo que el modelo no falle en producción si aparece una categoría nueva que no estaba en el entrenamiento.

Se forzó el tipo de dato str en las columnas categóricas antes de procesar para evitar errores de tipo en el pipeline automatizado.

3. Resultados del Avance 2
Se obtuvo el objeto preprocesador.pkl.

Este archivo encapsula toda la lógica de limpieza. Al exportarlo, garantizamos que los datos que lleguen a través de la API (FastAPI) se transformen exactamente igual que los datos históricos, eliminando el riesgo de Training-Serving Skew.

# 🤖 Avance 3: Modelado, Entrenamiento y Validación
El objetivo de esta fase fue identificar el algoritmo con mayor capacidad de generalización y preparar el modelo para su despliegue, enfrentando el desafío del desbalanceo de clases y la calidad de los datos.

1. Selección y Entrenamiento de Modelos
Se evaluaron múltiples arquitecturas, incluyendo Regresión Logística, Random Forest y XGBoost (seleccionado como modelo final), utilizando el pipeline de preprocesamiento del Avance 2.

Decisiones Estratégicas:

Elección de XGBoost: Se seleccionó este algoritmo por su capacidad nativa para manejar datos tabulares complejos y su robustez frente a valores atípicos que persistían en la data financiera.

Validación Cruzada (K-Fold): No nos basamos en una sola partición de datos. Implementamos validación cruzada para garantizar que las métricas de desempeño fueran consistentes en diferentes subconjuntos de la base de datos "imperfecta".

2. Evaluación con Enfoque en Negocio
Evaluación mediante matrices de confusión y métricas de precisión, recall y F1-Score.

Dado el desbalanceo en la variable Pago_atiempo, se priorizó el F1-Score sobre el Accuracy. Sabemos que un modelo puede ser 90% "preciso" simplemente prediciendo que todos pagarán, pero eso sería un desastre financiero. Buscamos el equilibrio entre detectar el riesgo y no rechazar buenos clientes.

3. Resultados del Avance 3
Se genero de modelo_riesgo.pkl.

con las métricas Logradas se alcanzó un nivel de predictibilidad sólido que supera el azar estadístico, validando que el preprocesamiento del Avance 2 logró extraer señales útiles de una fuente de datos originalmente ruidosa.

Se guardó el set data_referencia.csv (X_train procesado) para ser utilizado en el sistema de monitoreo de estabilidad (PSI/Drift).

# 🛠 Avance 4: Despliegue, Containerización y Monitoreo (MLOps)
El objetivo final fue transicionar del modelo estático a una infraestructura de microservicios robusta, garantizando la portabilidad y la vigilancia continua del rendimiento en producción.

1. Arquitectura de Microservicios con FastAPI
Se desarrolló el script model_deploy.py para exponer el modelo a través de una API REST.

Validación de Tipos con Pydantic: Se implementó un esquema de entrada estricto para asegurar que la API solo procese datos con el formato correcto, evitando caídas del servicio por datos malformados.

La API carga de forma independiente el preprocesador.pkl y el modelo_riesgo.pkl, permitiendo actualizar cualquiera de los dos componentes sin necesidad de reescribir el código base.

2. Containerización y Orquestación (Docker)
Creación de Dockerfile.api, Dockerfile.dashboard y docker-compose.yml.

Aislamiento de Entornos: Al usar Docker, garantizamos que el modelo corra exactamente igual en el servidor de Jenkins que en el entorno local.

Orquestación de Servicios: Con docker-compose, se gestiona la comunicación entre la API (el cerebro) y el Dashboard (la interfaz), creando una red interna segura para el flujo de datos.

3. Dashboard y Monitoreo de Salud (Drift Detection)
Implementación de una interfaz en Streamlit (app.py) y un sistema de monitoreo (model_monitoring.py).

Decisiones Estratégicas:

Detección de Data Drift: Se utilizó data_referencia.csv para comparar en tiempo real la distribución de los datos entrantes contra los de entrenamiento. Como Senior, sabemos que si el mercado financiero cambia, el modelo debe alertar sobre su propia obsolescencia.

Métricas de Estabilidad: Se incluyó el cálculo del PSI (Population Stability Index) para cuantificar qué tanto han cambiado los perfiles de los solicitantes de crédito.

4. Resultados Finales del Proyecto
Se entrega una solución que no solo predice el riesgo con alta fidelidad a pesar de la base de datos original ruidosa, sino que es capaz de auto-diagnosticarse y desplegarse automáticamente mediante pipelines de CI/CD.
