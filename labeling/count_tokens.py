import tiktoken
import json
import os

import argparse

def analizar_costos_jsonl(
    file_path: str, 
    encoding_name: str = "o200k_base", 
    price_input_per_1m: float = None, 
    price_output_per_1m: float = None
) -> dict:
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    try:
        encoding = tiktoken.get_encoding(encoding_name)
    except Exception as e:
        print(f"Error cargando el tokenizer '{encoding_name}': {e}")
        return {}

    total_input_tokens = 0
    total_output_tokens = 0 
    line_count = 0

    TOKENS_PER_MESSAGE = 3
    TOKENS_PER_REQUEST = 3

    print(f"🔄 Procesando {os.path.basename(file_path)} con '{encoding_name}'...\n")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            
            line_count += 1
            try:
                data = json.loads(line)
                body = data.get("body", {})
                
                # --- 1. Calcular Input Tokens (Messages) ---
                messages = body.get("messages", [])
                for msg in messages:
                    # --- CORRECCIÓN AQUÍ ---
                    # Obtenemos el contenido. Si es None o no es string, lo manejamos.
                    content = msg.get("content", "")
                    role = msg.get("role", "")
                    
                    # 1. Si es None, lo convertimos a string vacío
                    if content is None:
                        content = ""
                    # 2. Si es una lista (multimodal/imágenes), extraemos solo el texto
                    elif isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_parts.append(part.get("text", ""))
                        content = " ".join(text_parts)
                    # 3. Si es cualquier otra cosa (números, etc), forzamos string
                    elif not isinstance(content, str):
                        content = str(content)

                    # Validamos role también por seguridad
                    if not isinstance(role, str):
                        role = str(role) if role is not None else ""

                    total_input_tokens += len(encoding.encode(content))
                    total_input_tokens += len(encoding.encode(role))
                    total_input_tokens += TOKENS_PER_MESSAGE
                
                total_input_tokens += TOKENS_PER_REQUEST

                # --- 2. Calcular Input Tokens (Structured Outputs) ---
                if "response_format" in body:
                    rsp_fmt = body["response_format"]
                    fmt_str = json.dumps(rsp_fmt) 
                    total_input_tokens += len(encoding.encode(fmt_str))
                
            except json.JSONDecodeError:
                print(f"⚠️ Error al leer JSON en línea {line_count}")
            except Exception as e:
                print(f"⚠️ Error inesperado en línea {line_count}: {e}")

    total_tokens = total_input_tokens + total_output_tokens

    # --- Cálculos de Costos ---
    cost_input = 0.0
    cost_output = 0.0
    total_cost = 0.0
    
    if price_input_per_1m is not None:
        cost_input = (total_input_tokens / 1_000_000) * price_input_per_1m
    
    if price_output_per_1m is not None:
        cost_output = (total_output_tokens / 1_000_000) * price_output_per_1m
        
    total_cost = cost_input + cost_output

    # --- Print Bonito ---
    separator = "─" * 40
    print(f"📊 REPORTE DE TOKENS Y COSTOS")
    print(separator)
    print(f"{'Archivo':<20} : {os.path.basename(file_path)}")
    print(f"{'Líneas (Requests)':<20} : {line_count}")
    print(separator)
    print(f"{'TIPO':<15} | {'COUNT':<10} | {'PRECIO EST. ($)'}")
    print(separator)
    
    p_in_str = f"${cost_input:.4f}" if price_input_per_1m else "N/A"
    print(f"{'Input Tokens':<15} | {total_input_tokens:<10} | {p_in_str}")
    
    p_out_str = f"${cost_output:.4f}" if price_output_per_1m else "N/A"
    print(f"{'Output Tokens':<15} | {total_output_tokens:<10} | {p_out_str}")
    
    print(separator)
    p_total_str = f"${total_cost:.4f}" if (price_input_per_1m or price_output_per_1m) else "N/A"
    print(f"{'TOTAL':<15} | {total_tokens:<10} | {p_total_str}")
    print(separator + "\n")

    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": total_cost if (price_input_per_1m or price_output_per_1m) else None
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calcula los tokens y el costo estimado de un archivo JSONL para OpenAI Batch API."
    )

    parser.add_argument(
        "-f", "--file", 
        type=str, 
        required=True, 
        help="Ruta al archivo `.jsonl` a analizar."
    )
    parser.add_argument(
        "--encoding_name", 
        type=str, 
        default="o200k_base", 
        help="Nombre del encoding de tiktoken a utilizar (default: `o200k_base` para GPT-4o)."
    )
    parser.add_argument(
        "--input_price", 
        type=float, 
        default=None, 
        help="Precio en USD por cada 1 Millón de tokens de entrada."
    )
    parser.add_argument(
        "--output_price", 
        type=float, 
        default=None, 
        help="Precio en USD por cada 1 Millón de tokens de salida."
    )

    args = parser.parse_args()

    analizar_costos_jsonl(
        file_path=args.file, 
        encoding_name=args.encoding_name, 
        price_input_per_1m=args.input_price,
        price_output_per_1m=args.output_price
    )