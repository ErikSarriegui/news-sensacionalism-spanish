# 🏷️ News Labeling Pipeline: Clickbait & Sensationalism

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Batch_API-green?logo=openai&logoColor=white)](https://platform.openai.com/docs/guides/batch)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-yellow)](https://huggingface.co/)

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
