# 🏷️ News Labeling Pipeline: Clickbait & Sensationalism

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Batch_API-green?logo=openai&logoColor=white)](https://platform.openai.com/docs/guides/batch)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-yellow)](https://huggingface.co/datasets/eriksarriegui/news-sensacionalism-spanish)

> **Herramienta de etiquetado sintético** utilizada para generar el dataset de detección de desinformación en noticias (Clickbait y Sensacionalismo). Proyecto desarrollado como parte del TFM del Máster en Ciencia de Datos (UCM).

Este repositorio contiene el código necesario para procesar grandes volúmenes de noticias utilizando la **Batch API de OpenAI**, lo que permite reducir costes en un 50% y procesar millones de tokens de forma asíncrona.

---

## 🚀 Características

* **⚡ Eficiencia de Costes:** Script dedicado (`count_tokens.py`) para estimar el precio antes de lanzar el trabajo usando `tiktoken`.
* **🛠️ Salidas Estructuradas:** Uso de **Pydantic** para forzar respuestas JSON válidas (schemas definidos en `objects.py`).
* **🧠 Prompts Especializados:** Criterios lingüísticos definidos para detectar *Curiosity Gap* (Clickbait) y *Manipulación Emocional* (Sensacionalismo).
* **🔄 Pipeline Completo:** Desde la ingesta de archivos `.parquet` hasta la descarga de resultados `.jsonl`.

## 📂 Estructura del Proyecto

```bash
.
├── labeling/
│   ├── __init__.py
│   ├── create_job.py       # Sube el archivo y crea el Batch Job
│   ├── download_output.py  # Consulta estado y descarga resultados
│   ├── generate_file.py    # Convierte DataFrame a JSONL formato Batch
│   ├── count_tokens.py     # Estima tokens y costes
│   ├── objects.py          # Definición de modelos Pydantic (Output Parsers)
│   └── prompts.py          # Prompts de sistema para los agentes
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt        # Dependencias
└── README.md
```

## 🛠️ Instalación
1. **Clona el repositorio**:
```bash
git clone https://github.com/ErikSarriegui/news-sensacionalism-spanish
cd news-labeling-pipeline
```

2. **Instala las dependencias**:
```bash
pip install -r requirements.txt
```

## ⚙️ Uso del Pipeline
El proceso se divide en 4 pasos secuenciales. Asegúrate de tener un archivo .parquet con tus noticias como entrada.

1. **Generar archivo de Batch (`.jsonl`)**
Prepara los datos definiendo el modelo y el tipo de tarea (`clickbait` o `sensacionalism`):
```bash
python -m labeling.generate_file \
  --input_file "data/raw_news.parquet" \
  --output_file "batch_input.jsonl" \
  --type clickbait \
  --model "gpt-5-mini" \
  --text_column "texto"
```

2. **Analizar Costes (Opcional pero recomendado)**
Antes de enviar, calcula cuántos tokens consumirá el proceso para evitar sorpresas. Ten en cuenta que esto solo tomará en cuenta el número de tokens de entrada (input).
```bash
python -m labeling.count_tokens \
  --file "batch_input.jsonl" \
  --input_price 0.15 \
  --output_price 0.60
```

3. **Crear el Job en OpenAI**
Sube el archivo y lanza el proceso de etiquetado en la nube.
```bash
python -m labeling.create_job \
  --file "batch_input.jsonl" \
  --job_name "Etiquetado Clickbait V1"
```
> El script devolverá un BATCH_ID (ej. batch_abc123). Guárdalo.

4. **Descargar Resultados**
Una vez completado (puede tardar hasta 24h), descarga las etiquetas.
```bash
python -m labeling.download_output \
  --batch_id "batch_abc123..." \
  --output_file "resultados_etiquetados.jsonl"
```

## 🧠 Metodología de Etiquetado
El sistema utiliza dos enfoques distintos definidos en `prompts.py`:

### Validación
La calidad de los datos generados con este código ha sido validada comparando las etiquetas de `gpt-5-mini` contra un modelo superior (`gpt-5.2`) en un subset de control, obteniendo un Agreement Score del 96%.

## 🔗 Dataset
El dataset final generado con estas herramientas está disponible (con acceso restringido para evaluación académica) en Hugging Face:

🤗 [Ver Dataset en Hugging Face](https://huggingface.co/datasets/eriksarriegui/news-sensacionalism-spanish)

## 👥 Autores
* Erik Sarriegui
* Jesús Antonio Martínez
* Pablo Navarro
* Julen Neila
* Pedro Pablo Vicente
* Eduardo Corral

*Disclaimer: Este repositorio utiliza la API de OpenAI. Asegúrate de cumplir con sus políticas de uso y recuerda que eres responsable de los costes generados por la ejecución de estos scripts.*
