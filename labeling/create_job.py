from openai import OpenAI
import argparse

def create_batch_job(
        client : OpenAI,
        filename : str,
        batch_job_name : str = "Etiquetado de noticias",
) -> str:
    batch_input_file = client.files.create(
        file = open(filename, "rb"),
        purpose = "batch"
    )

    print(f"Archivo subido. ID: {batch_input_file.id}")

    batch_job = client.batches.create(
        input_file_id = batch_input_file.id,
        endpoint = "/v1/chat/completions",
        completion_window = "24h",
        metadata = {
            "description": batch_job_name
        }
    )

    print(f"Batch creado. Batch ID: {batch_job.id}\nAhora debes esperar a que se procese (puede tardar desde minutos a 24h).")

    return batch_job.id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sube un archivo JSONL a OpenAI y crea un Batch Job."
    )

    parser.add_argument(
        "-f", "--file", 
        type=str, 
        required=True, 
        help="Ruta al archivo `.jsonl` local que se va a subir."
    )

    parser.add_argument(
        "--job_name", 
        type=str, 
        default="Etiquetado de noticias", 
        help="Descripción (metadata) para identificar el Batch Job."
    )

    args = parser.parse_args()

    client = OpenAI()

    create_batch_job(
        client=client,
        filename=args.file,  # Corregido: en tu función se llama 'filename'
        batch_job_name=args.job_name
    )