import asyncio
import json
import argparse
import os
from openai import AsyncOpenAI
from tqdm.asyncio import tqdm
async def process_single_request(client: AsyncOpenAI, semaphore: asyncio.Semaphore, line_data: dict):
    """
    Procesa una única línea del archivo JSONL de entrada.
    Extrae el 'body' preparado para Batch y lo envía directamente a la API.
    """
    async with semaphore:
        custom_id = line_data.get("custom_id")
        body = line_data.get("body", {})
        
        try:
            model = body.get("model")
            messages = body.get("messages")
            response_format = body.get("response_format")
            temperature = body.get("temperature", 1.0)

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format,
                temperature=temperature
            )
            
            output_content = response.choices[0].message.content
            
            return {
                "id": f"batch_req_{custom_id}",
                "custom_id": custom_id,
                "response": {
                    "status_code": 200,
                    "request_id": response.id,
                    "body": {
                        "choices": [
                            {
                                "message": {
                                    "content": output_content,
                                    "role": "assistant"
                                }
                            }
                        ]
                    }
                },
                "error": None
            }

        except Exception as e:
            return {
                "id": f"batch_req_{custom_id}",
                "custom_id": custom_id,
                "response": None,
                "error": {
                    "message": str(e),
                    "code": "exception"
                }
            }

async def process_file(input_file: str, output_file: str, client: AsyncOpenAI, concurrency: int):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f if line.strip()]

    print(f"🚀 Iniciando procesamiento asíncrono de {len(lines)} registros.")
    print(f"⚡ Concurrencia máxima: {concurrency} peticiones simultáneas.")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    for line in lines:
        task = process_single_request(client, semaphore, line)
        tasks.append(task)

    results = await tqdm.gather(*tasks, desc="Procesando")

    with open(output_file, 'w', encoding='utf-8') as f:
        for res in results:
            f.write(json.dumps(res, ensure_ascii=False) + '\n')
            
    print(f"✅ Procesamiento completado. Resultados guardados en: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Procesa un archivo JSONL (formato Batch API) de forma síncrona/async usando AsyncOpenAI."
    )
    
    parser.add_argument("-i", "--input_file", type=str, required=True, help="Ruta al archivo batch_input.jsonl")
    parser.add_argument("-o", "--output_file", type=str, required=True, help="Ruta para guardar los resultados.")
    parser.add_argument("--base_url", type=str, default=None, help="Base URL personalizada (opcional).")
    parser.add_argument("--api_key", type=str, default=None, help="API Key (opcional, por defecto usa env var).")
    parser.add_argument("--concurrency", type=int, default=10, help="Número máximo de peticiones simultáneas (default: 10).")

    args = parser.parse_args()

    # Configuración del cliente
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("No se encontró OPENAI_API_KEY. Configúrala en .env o pásala como argumento.")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=args.base_url
    )

    try:
        asyncio.run(process_file(
            input_file=args.input_file, 
            output_file=args.output_file, 
            client=client, 
            concurrency=args.concurrency
        ))
    except KeyboardInterrupt:
        print("\n🛑 Proceso interrumpido por el usuario.")