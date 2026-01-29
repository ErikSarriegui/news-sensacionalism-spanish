import pandas as pd
import json

import argparse

try:
    from .prompts import CLICKBAIT_PROMPT, SENSACIONALISM_PROMPT
    from .objects import ClickbaitAnalysis, SensationalismAnalysis
    
except ImportError:
    from prompts import CLICKBAIT_PROMPT, SENSACIONALISM_PROMPT
    from objects import ClickbaitAnalysis, SensationalismAnalysis

def generate_file(
        filename : str,
        model : str,
        prompt : str,
        json_schema : dict,
        nombre_schema : str,
        df : pd.DataFrame,
        text_column : str = "texto"
) -> str:
    dataset = df.to_dict(orient="records")

    with open(filename, 'w', encoding='utf-8') as f:
        for item in dataset:
            request_body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": item[text_column]}
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": nombre_schema,
                        "schema": json_schema,
                        "strict": True
                    }
                }
            }
            
            batch_request = {
                "custom_id": item["id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": request_body
            }
            
            f.write(json.dumps(batch_request, ensure_ascii=False) + '\n')

    print(f"Archivo '{filename}' creado exitosamente.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Genera un archivo JSONL listo para Batch API a partir de un dataset Parquet."
    )

    parser.add_argument(
        "-i", "--input_file", 
        type=str, 
        required=True, 
        help="Ruta al archivo `.parquet` de origen."
    )
    parser.add_argument(
        "-o", "--output_file", 
        type=str, 
        required=True, 
        help="Ruta donde se guardará el archivo `.jsonl` generado."
    )
    parser.add_argument(
        "-m", "--model", 
        type=str, 
        required=True,
        default="gpt-5-mini",
        help="Modelo de OpenAI a utilizar (ej. `gpt-5-mini`)."
    )
    parser.add_argument(
        "-t", "--type", 
        type=str, 
        required=True, 
        choices=["clickbait", "sensacionalism"], 
        help="Tipo de análisis a realizar: 'clickbait' o 'sensacionalism'."
    )
    parser.add_argument(
        "--text_column", 
        type=str, 
        default="texto", 
        help="Nombre de la columna en el Parquet que contiene el texto a analizar."
    )

    args = parser.parse_args()

    df = pd.read_parquet(args.input_file)

    if args.type == "clickbait":
        prompt = CLICKBAIT_PROMPT
        json_schema = ClickbaitAnalysis.model_json_schema()
        nombre_schema = "clickbait_analysis_schema"
    
    elif args.type == "sensacionalism":
        prompt = SENSACIONALISM_PROMPT
        json_schema = SensationalismAnalysis.model_json_schema()
        nombre_schema = "sensationalism_analysis_schema"

    generate_file(
        filename=args.output_file,
        model=args.model,
        prompt=prompt,
        json_schema=json_schema,
        nombre_schema=nombre_schema,
        df=df,
        text_column=args.text_column
    )