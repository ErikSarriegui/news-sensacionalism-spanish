import asyncio
import json
import argparse
import os
from openai import AsyncOpenAI, AsyncAzureOpenAI
from tqdm.asyncio import tqdm

async def process_single_request(client, semaphore: asyncio.Semaphore, line_data: dict, override_model: str = None):
    """
    Procesa una línea. Si override_model está definido (común en Azure), 
    ignora el modelo del JSONL y usa el nombre del despliegue de Azure.
    """
    async with semaphore:
        custom_id = line_data.get("custom_id")
        body = line_data.get("body", {})
        
        try:
            model = override_model if override_model else body.get("model")
            
            messages = body.get("messages")
            response_format = body.get("response_format")
            temperature = body.get("temperature", 1.0)
            max_tokens = body.get("max_tokens")

            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens
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

async def process_file(input_file: str, output_file: str, client, concurrency: int, override_model: str = None):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [json.loads(line) for line in f if line.strip()]

    print(f"🚀 Iniciando procesamiento ({type(client).__name__})")
    print(f"📄 Registros: {len(lines)} | ⚡ Concurrencia: {concurrency}")
    if override_model:
        print(f"⚠️  Forzando modelo/deployment: '{override_model}'")

    semaphore = asyncio.Semaphore(concurrency)
    tasks = []

    for line in lines:
        task = process_single_request(client, semaphore, line, override_model)
        tasks.append(task)

    results = await tqdm.gather(*tasks, desc="Procesando")

    with open(output_file, 'w', encoding='utf-8') as f:
        for res in results:
            f.write(json.dumps(res, ensure_ascii=False) + '\n')
            
    print(f"✅ Completado. Guardado en: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesa JSONL de manera asíncrona (Compatible Azure/OpenAI).")
    
    parser.add_argument("-i", "--input_file", type=str, required=True, help="Archivo batch_input.jsonl")
    parser.add_argument("-o", "--output_file", type=str, required=True, help="Archivo de salida")
    parser.add_argument("--concurrency", type=int, default=10, help="Peticiones simultáneas")
    parser.add_argument("--provider", type=str, choices=["openai", "azure"], default="openai", help="Proveedor de API.")
    parser.add_argument("--api_key", type=str, default=None, help="API Key (o usa env vars).")
    parser.add_argument("--azure_endpoint", type=str, default=None, help="Endpoint de Azure (ej. https://mi-recurso.openai.azure.com/).")
    parser.add_argument("--api_version", type=str, default="2024-02-15-preview", help="Versión de API de Azure.")
    parser.add_argument("--base_url", type=str, default=None, help="Base URL para cliente estándar OpenAI.")
    parser.add_argument("--force_model", type=str, default=None, help="Si se especifica, usa este nombre de modelo/deployment ignorando el del JSONL.")

    args = parser.parse_args()

    api_key = args.api_key or os.getenv("OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("❌ Falta la API Key. Configura OPENAI_API_KEY o AZURE_OPENAI_API_KEY.")

    if args.provider == "azure":
        if not args.azure_endpoint and not os.getenv("AZURE_OPENAI_ENDPOINT"):
             raise ValueError("❌ Para Azure necesitas --azure_endpoint o env var AZURE_OPENAI_ENDPOINT.")
        
        endpoint = args.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        
        client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=args.api_version,
            azure_endpoint=endpoint
        )
    else:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=args.base_url
        )

    try:
        asyncio.run(process_file(
            input_file=args.input_file, 
            output_file=args.output_file, 
            client=client, 
            concurrency=args.concurrency,
            override_model=args.force_model
        ))
    except KeyboardInterrupt:
        print("\n🛑 Detenido por el usuario.")