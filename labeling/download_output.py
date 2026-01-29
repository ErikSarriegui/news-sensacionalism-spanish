from openai import OpenAI
import argparse

def download_batch_output(
        client : OpenAI,
        batch_id: str,
        output_filename: str
) -> None:
    try:
        batch_status = client.batches.retrieve(batch_id)
    except Exception as e:
        print(f"Error al intentar recuperar el batch '{batch_id}': {e}")
        return

    print(f"Estado del Batch: {batch_status.status}")

    if batch_status.status == "completed":
        print("¡Proceso completado! Descargando resultados...")
        
        output_file_id = batch_status.output_file_id
        
        if not output_file_id:
            print("Error: El batch está completado pero no tiene 'output_file_id'.")
            return

        try:
            file_response = client.files.content(output_file_id)
            content = file_response.text
            
            with open(output_filename, "w", encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Resultados guardados exitosamente en '{output_filename}'")
        except Exception as e:
            print(f"Error al descargar o guardar el archivo: {e}")

    elif batch_status.status == "failed":
        print("❌ El proceso falló.")
        if batch_status.errors:
            print("Errores reportados:")
            for error in batch_status.errors:
                print(f" - {error}")
    
    elif batch_status.status in ["in_progress", "validating", "finalizing"]:
        print("⏳ El proceso aún está en curso. Inténtalo de nuevo más tarde.")
    
    else:
        print(f"El proceso está en estado: {batch_status.status}")

if __name__ == "__main__":    
    parser = argparse.ArgumentParser(
        description="Verifica el estado de un Batch Job de OpenAI y descarga los resultados si está completado."
    )

    parser.add_argument(
        "--batch_id", 
        type=str, 
        required=True, 
        help="El ID del Batch Job a consultar (ej. `batch_abc123...`)."
    )
    parser.add_argument(
        "-o", "--output_file", 
        type=str, 
        required=True, 
        help="Ruta y nombre del archivo `.jsonl` donde se guardarán los resultados."
    )

    args = parser.parse_args()

    client = OpenAI()

    download_batch_output(
        client = client,
        batch_id = args.batch_id,
        output_filename = args.output_file
    )